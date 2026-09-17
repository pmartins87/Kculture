// Kculture L2 VecGame: batched exact Kaggriculture simulations for RL/search.
//
// This file deliberately depends on the pinned Apache-2.0 kagsim simulator
// checked out under external/kaggriculture-cppsim.  It does NOT change game
// semantics.  It only removes per-environment Python callbacks by transporting
// observations/actions as dense numpy tensors.

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <atomic>
#include <cstdint>
#include <thread>
#include <vector>

#include "sim.hpp"

namespace py = pybind11;
using namespace kag;

namespace {

constexpr int RAW_ORDER_SLOTS = 16;
constexpr int ACTION_WIDTH = 1 + MAX_UNITS * 3 + 1 + RAW_ORDER_SLOTS * 3;
constexpr int GLOBAL_WIDTH = 37;
constexpr int TILE_WIDTH = 12;
constexpr int UNIT_WIDTH = 3;
constexpr int PRIVATE_WIDTH = N_ITEMS + N_CROPS + MAX_UNITS * N_ITEMS;

inline int clampi(int x, int lo, int hi) {
    return std::max(lo, std::min(hi, x));
}

Action decode_action_row(const int32_t* row) {
    Action a;
    a.clear();

    int nu = clampi(static_cast<int>(row[0]), 1, MAX_UNITS);
    a.n_units = nu;
    for (int u = 0; u < nu; ++u) {
        int off = 1 + u * 3;
        int op = static_cast<int>(row[off + 0]);
        int arg = static_cast<int>(row[off + 1]);
        int n = static_cast<int>(row[off + 2]);
        a.units[u].op = static_cast<uint8_t>((op >= 0 && op <= OP_INVALID) ? op : OP_INVALID);
        a.units[u].arg = static_cast<uint8_t>((arg >= 0 && arg < N_ITEMS) ? arg : 255);
        a.units[u].n = static_cast<int16_t>(clampi(n, -32768, 32767));
    }

    int order_base = 1 + MAX_UNITS * 3;
    int no = clampi(static_cast<int>(row[order_base]), 0, RAW_ORDER_SLOTS);
    a.n_orders = no;
    for (int o = 0; o < no; ++o) {
        int off = order_base + 1 + o * 3;
        int op = static_cast<int>(row[off + 0]);
        int item = static_cast<int>(row[off + 1]);
        int n = static_cast<int>(row[off + 2]);
        a.orders[o].op = static_cast<uint8_t>((op >= M_NONE && op <= M_SELL) ? op : M_NONE);
        a.orders[o].item = static_cast<uint8_t>((item >= 0 && item < N_ITEMS) ? item : 255);
        a.orders[o].n = static_cast<int32_t>(n);
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

}  // namespace

class VecGame {
public:
    explicit VecGame(const std::vector<uint64_t>& seeds, int steps = 720) {
        reset(seeds, steps);
    }

    void reset(const std::vector<uint64_t>& seeds, int steps = 720) {
        steps_ = steps;
        sims_.clear();
        sims_.reserve(seeds.size());
        for (uint64_t seed : seeds) {
            Config c;
            c.seed = seed;
            c.episode_steps = steps;
            sims_.emplace_back(c);
        }
    }

    size_t size() const { return sims_.size(); }

    py::array_t<uint8_t> done_mask() const {
        py::array_t<uint8_t> out({static_cast<py::ssize_t>(sims_.size())});
        auto* p = out.mutable_data();
        for (size_t i = 0; i < sims_.size(); ++i) p[i] = sims_[i].st.done ? 1 : 0;
        return out;
    }

    py::array_t<double> rewards() const {
        py::array_t<double> out({static_cast<py::ssize_t>(sims_.size()), static_cast<py::ssize_t>(2)});
        auto* p = out.mutable_data();
        for (size_t i = 0; i < sims_.size(); ++i) {
            p[i * 2 + 0] = sims_[i].reward(0);
            p[i * 2 + 1] = sims_[i].reward(1);
        }
        return out;
    }

    py::dict observe(int player) const {
        if (player != 0 && player != 1) throw std::invalid_argument("player must be 0 or 1");
        const py::ssize_t B = static_cast<py::ssize_t>(sims_.size());

        py::array_t<float> global(std::vector<py::ssize_t>{B, GLOBAL_WIDTH});
        py::array_t<int16_t> tiles(std::vector<py::ssize_t>{B, 2, BOARD, BOARD, TILE_WIDTH});
        py::array_t<int16_t> units(std::vector<py::ssize_t>{B, 2, MAX_UNITS, UNIT_WIDTH});
        py::array_t<int16_t> priv(std::vector<py::ssize_t>{B, PRIVATE_WIDTH});

        float* gp = global.mutable_data();
        int16_t* tp = tiles.mutable_data();
        int16_t* up = units.mutable_data();
        int16_t* pp = priv.mutable_data();

        std::fill(gp, gp + static_cast<size_t>(B) * GLOBAL_WIDTH, 0.0f);
        std::fill(tp, tp + static_cast<size_t>(B) * 2 * BOARD * BOARD * TILE_WIDTH, static_cast<int16_t>(0));
        std::fill(up, up + static_cast<size_t>(B) * 2 * MAX_UNITS * UNIT_WIDTH, static_cast<int16_t>(0));
        std::fill(pp, pp + static_cast<size_t>(B) * PRIVATE_WIDTH, static_cast<int16_t>(0));

        for (py::ssize_t bi = 0; bi < B; ++bi) {
            const Sim& sim = sims_[static_cast<size_t>(bi)];
            const State& st = sim.st;
            const int own = player;
            const int opp = 1 - player;
            const Farm& fo = st.farms[own];
            const Farm& fx = st.farms[opp];

            float* g = gp + bi * GLOBAL_WIDTH;
            int gi = 0;
            g[gi++] = static_cast<float>(st.step);
            g[gi++] = static_cast<float>(st.day);
            g[gi++] = static_cast<float>(st.hour);
            g[gi++] = static_cast<float>(fo.money);
            g[gi++] = static_cast<float>(fx.money);
            g[gi++] = static_cast<float>(fo.n_units);
            g[gi++] = static_cast<float>(fx.n_units);
            g[gi++] = static_cast<float>(fo.n_quadrants);
            g[gi++] = static_cast<float>(fx.n_quadrants);
            g[gi++] = static_cast<float>(fo.hires_today);
            g[gi++] = static_cast<float>(fx.hires_today);
            for (int i = 0; i < N_PRODUCTS; ++i) g[gi++] = static_cast<float>(st.market.inventory[i]);
            for (int i = 0; i < N_PRODUCTS; ++i) g[gi++] = static_cast<float>(st.market.prices[i]);
            int shop_counts[N_SHOPS] = {0};
            for (int i = 0; i < st.n_shops; ++i) {
                int s = st.shops[i];
                if (s >= 0 && s < N_SHOPS) shop_counts[s] += 1;
            }
            for (int i = 0; i < N_SHOPS; ++i) g[gi++] = static_cast<float>(shop_counts[i]);

            for (int rel = 0; rel < 2; ++rel) {
                const int abs_p = rel == 0 ? own : opp;
                const Farm& f = st.farms[abs_p];
                for (int y = 0; y < BOARD; ++y) {
                    for (int x = 0; x < BOARD; ++x) {
                        const Tile& t = f.tiles[y][x];
                        size_t base = (((static_cast<size_t>(bi) * 2 + rel) * BOARD + y) * BOARD + x) * TILE_WIDTH;
                        int16_t what = -1;
                        if (t.kind == T_PLANT || ((t.kind == T_COOP || t.kind == T_PASTURE) && t.has_animal))
                            what = static_cast<int16_t>(t.what);
                        tp[base + 0] = static_cast<int16_t>(t.kind);
                        tp[base + 1] = what;
                        tp[base + 2] = static_cast<int16_t>(t.has_animal);
                        tp[base + 3] = static_cast<int16_t>(t.watered_today);
                        tp[base + 4] = static_cast<int16_t>(t.fed_today);
                        tp[base + 5] = static_cast<int16_t>(t.cared_today);
                        tp[base + 6] = static_cast<int16_t>(t.fertilizer_available);
                        tp[base + 7] = static_cast<int16_t>(t.consecutive_dry);
                        tp[base + 8] = static_cast<int16_t>(t.yield_units);
                        tp[base + 9] = static_cast<int16_t>(t.planted_day);
                        tp[base + 10] = static_cast<int16_t>(t.max_lifespan_step);
                        tp[base + 11] = static_cast<int16_t>(t.fertilized_until_day);
                    }
                }
                for (int u = 0; u < MAX_UNITS; ++u) {
                    size_t base = ((static_cast<size_t>(bi) * 2 + rel) * MAX_UNITS + u) * UNIT_WIDTH;
                    if (u < f.n_units) {
                        up[base + 0] = static_cast<int16_t>(f.pos_x[u]);
                        up[base + 1] = static_cast<int16_t>(f.pos_y[u]);
                        up[base + 2] = 1;
                    } else {
                        up[base + 0] = -1;
                        up[base + 1] = -1;
                        up[base + 2] = 0;
                    }
                }
            }

            int pi = 0;
            for (int i = 0; i < N_ITEMS; ++i) pp[static_cast<size_t>(bi) * PRIVATE_WIDTH + pi++] = fo.shed[i];
            for (int i = 0; i < N_CROPS; ++i) pp[static_cast<size_t>(bi) * PRIVATE_WIDTH + pi++] = fo.seeds[i];
            for (int u = 0; u < MAX_UNITS; ++u)
                for (int i = 0; i < N_ITEMS; ++i)
                    pp[static_cast<size_t>(bi) * PRIVATE_WIDTH + pi++] = fo.inv[u][i];
        }

        py::dict out;
        out["global"] = std::move(global);
        out["tiles"] = std::move(tiles);
        out["units"] = std::move(units);
        out["private"] = std::move(priv);
        return out;
    }

    void step(py::array_t<int32_t, py::array::c_style | py::array::forcecast> a0,
              py::array_t<int32_t, py::array::c_style | py::array::forcecast> a1,
              int threads = 0) {
        auto b0 = a0.request();
        auto b1 = a1.request();
        const size_t B = sims_.size();
        if (b0.ndim != 2 || b1.ndim != 2 ||
            b0.shape[0] != static_cast<py::ssize_t>(B) || b1.shape[0] != static_cast<py::ssize_t>(B) ||
            b0.shape[1] != ACTION_WIDTH || b1.shape[1] != ACTION_WIDTH)
            throw std::invalid_argument("actions must have shape [B, ACTION_WIDTH]");

        const int32_t* p0 = static_cast<const int32_t*>(b0.ptr);
        const int32_t* p1 = static_cast<const int32_t*>(b1.ptr);
        std::vector<Action> x0(B), x1(B);
        for (size_t i = 0; i < B; ++i) {
            x0[i] = decode_action_row(p0 + i * ACTION_WIDTH);
            x1[i] = decode_action_row(p1 + i * ACTION_WIDTH);
        }

        py::gil_scoped_release release;
        parallel_for(B, threads, [&](size_t i) {
            sims_[i].step(x0[i], x1[i]);
        });
    }

private:
    int steps_ = 720;
    std::vector<Sim> sims_;
};

PYBIND11_MODULE(kagvec, m) {
    m.doc() = "Kculture L2 vectorized wrapper over bit-exact Kaggriculture kagsim";
    py::class_<VecGame>(m, "VecGame")
        .def(py::init<const std::vector<uint64_t>&, int>(), py::arg("seeds"), py::arg("steps") = 720)
        .def("reset", &VecGame::reset, py::arg("seeds"), py::arg("steps") = 720)
        .def_property_readonly("size", &VecGame::size)
        .def("observe", &VecGame::observe, py::arg("player"))
        .def("step", &VecGame::step, py::arg("actions0"), py::arg("actions1"), py::arg("threads") = 0)
        .def("done_mask", &VecGame::done_mask)
        .def("rewards", &VecGame::rewards);

    m.attr("ACTION_WIDTH") = ACTION_WIDTH;
    m.attr("GLOBAL_WIDTH") = GLOBAL_WIDTH;
    m.attr("TILE_WIDTH") = TILE_WIDTH;
    m.attr("UNIT_WIDTH") = UNIT_WIDTH;
    m.attr("PRIVATE_WIDTH") = PRIVATE_WIDTH;
    m.attr("MAX_UNITS") = MAX_UNITS;
    m.attr("MAX_ORDER_SLOTS") = RAW_ORDER_SLOTS;
    m.attr("ENGINE_VERSION") = "1.32.7";
    m.attr("SCHEMA") = "kculture-l2-v0";
}
