#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <functional>
#include <thread>
#include <vector>

#include "sim.hpp"

namespace py = pybind11;
using namespace kag;

namespace {

constexpr int ORDER_SLOTS = 16;
constexpr int ACTION_WIDTH = 1 + MAX_UNITS * 3 + 1 + ORDER_SLOTS * 3;
constexpr int FEATURE_WIDTH = 114;

inline int clampi(int x, int lo, int hi) {
    return std::max(lo, std::min(hi, x));
}

Action decode(const int32_t* row) {
    Action a;
    a.clear();
    int nu = clampi(static_cast<int>(row[0]), 1, MAX_UNITS);
    a.n_units = nu;
    for (int u = 0; u < nu; ++u) {
        int off = 1 + u * 3;
        int op = row[off];
        int arg = row[off + 1];
        int n = row[off + 2];
        a.units[u].op = static_cast<uint8_t>((op >= 0 && op <= OP_INVALID) ? op : OP_INVALID);
        a.units[u].arg = static_cast<uint8_t>((arg >= 0 && arg < N_ITEMS) ? arg : 255);
        a.units[u].n = static_cast<int16_t>(clampi(n, -32768, 32767));
    }

    int base = 1 + MAX_UNITS * 3;
    int no = clampi(static_cast<int>(row[base]), 0, ORDER_SLOTS);
    a.n_orders = no;
    for (int j = 0; j < no; ++j) {
        int off = base + 1 + j * 3;
        int op = row[off];
        int item = row[off + 1];
        int n = row[off + 2];
        a.orders[j].op = static_cast<uint8_t>((op >= M_NONE && op <= M_SELL) ? op : M_NONE);
        a.orders[j].item = static_cast<uint8_t>((item >= 0 && item < N_ITEMS) ? item : 255);
        a.orders[j].n = n;
    }
    return a;
}

void parallel_for(size_t n, int threads, const std::function<void(size_t)>& fn) {
    if (n == 0) return;
    unsigned hw = std::thread::hardware_concurrency();
    int nt = threads > 0 ? threads : static_cast<int>(hw ? hw : 1u);
    nt = std::max(1, std::min<int>(nt, static_cast<int>(n)));
    if (nt == 1) {
        for (size_t i = 0; i < n; ++i) fn(i);
        return;
    }
    std::atomic<size_t> next{0};
    std::vector<std::thread> pool;
    pool.reserve(nt);
    for (int t = 0; t < nt; ++t) {
        pool.emplace_back([&]() {
            for (;;) {
                size_t i = next.fetch_add(1, std::memory_order_relaxed);
                if (i >= n) return;
                fn(i);
            }
        });
    }
    for (auto& th : pool) th.join();
}

std::vector<std::vector<Action>> decode_bank(const int32_t* p, size_t n, int turns) {
    std::vector<std::vector<Action>> out(n, std::vector<Action>(turns));
    for (size_t i = 0; i < n; ++i) {
        for (int t = 0; t < turns; ++t) {
            out[i][t] = decode(p + (i * static_cast<size_t>(turns) + t) * ACTION_WIDTH);
        }
    }
    return out;
}

void fill_features(const Sim& sim, int player, float* f) {
    const State& st = sim.st;
    const Farm& own = st.farms[player];
    const Farm& opp = st.farms[1 - player];
    int k = 0;

    f[k++] = static_cast<float>(st.step);
    f[k++] = static_cast<float>(st.day);
    f[k++] = static_cast<float>(st.hour);
    f[k++] = static_cast<float>(own.money);
    f[k++] = static_cast<float>(opp.money);
    f[k++] = static_cast<float>(own.n_units);
    f[k++] = static_cast<float>(opp.n_units);
    f[k++] = static_cast<float>(own.n_quadrants);
    f[k++] = static_cast<float>(opp.n_quadrants);
    f[k++] = static_cast<float>(own.hires_today);
    f[k++] = static_cast<float>(opp.hires_today);

    for (int i = 0; i < N_PRODUCTS; ++i) f[k++] = static_cast<float>(st.market.inventory[i]);
    for (int i = 0; i < N_PRODUCTS; ++i) f[k++] = static_cast<float>(st.market.prices[i]);

    int shop_counts[N_SHOPS] = {0};
    for (int i = 0; i < st.n_shops; ++i) {
        int s = st.shops[i];
        if (s >= 0 && s < N_SHOPS) shop_counts[s] += 1;
    }
    for (int i = 0; i < N_SHOPS; ++i) f[k++] = static_cast<float>(shop_counts[i]);

    for (int rel = 0; rel < 2; ++rel) {
        const Farm& x = st.farms[rel == 0 ? player : 1 - player];
        float kinds[6] = {0};
        float what[N_ITEMS] = {0};
        float sums[6] = {0};
        for (int y = 0; y < BOARD; ++y) {
            for (int xx = 0; xx < BOARD; ++xx) {
                const Tile& t = x.tiles[y][xx];
                int kind = static_cast<int>(t.kind);
                if (kind >= 0 && kind < 6) kinds[kind] += 1.0f;
                if (t.kind == T_PLANT || ((t.kind == T_COOP || t.kind == T_PASTURE) && t.has_animal)) {
                    int w = static_cast<int>(t.what);
                    if (w >= 0 && w < N_ITEMS) what[w] += 1.0f;
                }
                sums[0] += static_cast<float>(t.yield_units);
                sums[1] += static_cast<float>(t.consecutive_dry);
                sums[2] += t.watered_today ? 1.0f : 0.0f;
                sums[3] += t.fed_today ? 1.0f : 0.0f;
                sums[4] += t.cared_today ? 1.0f : 0.0f;
                sums[5] += t.fertilizer_available ? 1.0f : 0.0f;
            }
        }
        for (float v : kinds) f[k++] = v;
        for (float v : what) f[k++] = v;
        for (float v : sums) f[k++] = v;
    }

    for (int i = 0; i < N_ITEMS; ++i) f[k++] = static_cast<float>(own.shed[i]);
    for (int i = 0; i < N_CROPS; ++i) f[k++] = static_cast<float>(own.seeds[i]);
    for (int i = 0; i < N_ITEMS; ++i) {
        int total = 0;
        for (int u = 0; u < own.n_units; ++u) total += own.inv[u][i];
        f[k++] = static_cast<float>(total);
    }

    if (k != FEATURE_WIDTH) throw std::runtime_error("feature width mismatch");
}

}  // namespace

PYBIND11_MODULE(kagprog, m) {
    m.doc() = "Kculture exact tape-matrix and prefix-state evaluator";

    m.def("evaluate_matrix",
        [](py::array_t<int32_t, py::array::c_style | py::array::forcecast> tapes,
           py::array_t<int32_t, py::array::c_style | py::array::forcecast> opponents,
           const std::vector<uint64_t>& seeds,
           int threads) {
            auto tb = tapes.request();
            auto ob = opponents.request();
            if (tb.ndim != 3 || ob.ndim != 3 ||
                tb.shape[1] < 719 || ob.shape[1] < 719 ||
                tb.shape[2] != ACTION_WIDTH || ob.shape[2] != ACTION_WIDTH) {
                throw std::invalid_argument("tapes/opponents must be [N,>=719,170]");
            }

            size_t N = static_cast<size_t>(tb.shape[0]);
            size_t M = static_cast<size_t>(ob.shape[0]);
            size_t S = seeds.size();
            if (N == 0 || M == 0 || S == 0) throw std::invalid_argument("empty tape bank or seed list");

            constexpr int T = 719;
            auto A = decode_bank(static_cast<const int32_t*>(tb.ptr), N, T);
            auto B = decode_bank(static_cast<const int32_t*>(ob.ptr), M, T);

            py::array_t<float> out({
                static_cast<py::ssize_t>(N),
                static_cast<py::ssize_t>(M),
                static_cast<py::ssize_t>(S),
                static_cast<py::ssize_t>(2)
            });
            float* p = out.mutable_data();
            size_t jobs = N * M * S * 2;

            auto t0 = std::chrono::steady_clock::now();
            {
                py::gil_scoped_release release;
                parallel_for(jobs, threads, [&](size_t q) {
                    int seat = static_cast<int>(q % 2); q /= 2;
                    size_t si = q % S; q /= S;
                    size_t j = q % M;
                    size_t i = q / M;

                    Config c;
                    c.seed = seeds[si];
                    c.episode_steps = 720;
                    Sim sim(c);
                    while (!sim.st.done) {
                        int t = std::min(718, sim.st.step);
                        Action a0 = seat == 0 ? A[i][t] : B[j][t];
                        Action a1 = seat == 1 ? A[i][t] : B[j][t];
                        sim.step(a0, a1);
                    }
                    p[(((i * M + j) * S + si) * 2 + seat)] =
                        static_cast<float>(sim.reward(seat) - sim.reward(1 - seat));
                });
            }
            double sec = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
            py::dict d;
            d["margin"] = std::move(out);
            d["seconds"] = sec;
            d["episodes_per_second"] = jobs / std::max(1e-9, sec);
            return d;
        },
        py::arg("tapes"), py::arg("opponents"), py::arg("seeds"), py::arg("threads") = 0);

    m.def("prefix_features",
        [](py::array_t<int32_t, py::array::c_style | py::array::forcecast> base,
           py::array_t<int32_t, py::array::c_style | py::array::forcecast> opponents,
           const std::vector<uint64_t>& seeds,
           int checkpoint,
           int threads) {
            auto bb = base.request();
            auto ob = opponents.request();
            if (bb.ndim != 2 || bb.shape[0] < 719 || bb.shape[1] != ACTION_WIDTH ||
                ob.ndim != 3 || ob.shape[1] < 719 || ob.shape[2] != ACTION_WIDTH) {
                throw std::invalid_argument("base must be [>=719,170], opponents [M,>=719,170]");
            }
            if (checkpoint < 0 || checkpoint > 719) throw std::invalid_argument("checkpoint out of range");

            size_t M = static_cast<size_t>(ob.shape[0]);
            size_t S = seeds.size();
            if (M == 0 || S == 0) throw std::invalid_argument("empty opponents or seeds");

            constexpr int T = 719;
            std::vector<Action> A(T);
            const int32_t* bp = static_cast<const int32_t*>(bb.ptr);
            for (int t = 0; t < T; ++t) A[t] = decode(bp + t * ACTION_WIDTH);
            auto B = decode_bank(static_cast<const int32_t*>(ob.ptr), M, T);

            size_t jobs = M * S * 2;
            py::array_t<float> out({
                static_cast<py::ssize_t>(jobs),
                static_cast<py::ssize_t>(FEATURE_WIDTH)
            });
            float* p = out.mutable_data();

            {
                py::gil_scoped_release release;
                parallel_for(jobs, threads, [&](size_t q) {
                    size_t original = q;
                    int seat = static_cast<int>(q % 2); q /= 2;
                    size_t si = q % S; q /= S;
                    size_t j = q % M;

                    Config c;
                    c.seed = seeds[si];
                    c.episode_steps = 720;
                    Sim sim(c);
                    while (!sim.st.done && sim.st.step < checkpoint) {
                        int t = std::min(718, sim.st.step);
                        Action a0 = seat == 0 ? A[t] : B[j][t];
                        Action a1 = seat == 1 ? A[t] : B[j][t];
                        sim.step(a0, a1);
                    }
                    fill_features(sim, seat, p + original * FEATURE_WIDTH);
                });
            }
            return out;
        },
        py::arg("base"), py::arg("opponents"), py::arg("seeds"),
        py::arg("checkpoint"), py::arg("threads") = 0);

    m.attr("ACTION_WIDTH") = ACTION_WIDTH;
    m.attr("FEATURE_WIDTH") = FEATURE_WIDTH;
    m.attr("ENGINE_VERSION") = "1.32.7";
    m.attr("SCHEMA") = "kculture-programme-search-v0";
}
