// Kculture native adaptive teacher/search arena for Kaggriculture 1.32.7.
//
// Purpose: keep BOTH policy execution and exact environment stepping in C++ so
// strategic search does not fall back to 720 Python callbacks per episode.
// The controller is intentionally PARAMETRIC rather than a list of named macro
// plans: 32 independent continuous controls shape livestock, crops, labour,
// reserves, logistics, sell timing, opponent response and terminal behaviour.
// It is a bootstrap SEARCH TEACHER, not the final learned policy.
//
// Game semantics come exclusively from the pinned Apache-2.0 kagsim sim.hpp.
// The controller reads only current state that is legal/public for its seat plus
// its own private inventory; it never reads cfg.seed or future RNG.

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <functional>
#include <limits>
#include <thread>
#include <vector>

#include "sim.hpp"

namespace py = pybind11;
using namespace kag;

namespace {

constexpr int P = 32;

inline double clip01(double x) { return std::max(0.0, std::min(1.0, x)); }
inline int iround(double x) { return static_cast<int>(std::lround(x)); }
inline int manhattan(int x, int y, int tx, int ty) { return std::abs(x-tx) + std::abs(y-ty); }

struct Params {
    std::array<double, P> z{};
    explicit Params(const double* p) { for (int i=0;i<P;++i) z[i]=clip01(p[i]); }

    int cow_max() const { return iround(12*z[0]); }
    int sheep_max() const { return iround(8*z[1]); }
    int goose_max() const { return iround(8*z[2]); }
    int crop_max(int c) const {
        static const int mx[5] = {18, 10, 10, 10, 16};
        return iround(mx[c]*z[3+c]);
    }
    int hands() const { return 2 + iround(10*z[8]); }
    int lands() const { return 1 + iround(3*z[9]); }
    double reserve() const { return 50.0 + 1750.0*z[10]; }
    double wheat_per_animal() const { return 1.0 + 4.0*z[11]; }
    int feed_prio() const { return 100 + iround(45*z[12]); }
    int care_prio() const { return 45 + iround(65*z[13]); }
    int harvest_trigger() const { return 1 + iround(5*z[14]); }
    int fert_prio() const { return 35 + iround(65*z[15]); }
    double sell_common() const { return 0.70 + 0.70*z[16]; }
    double sell_factor(int product) const { return 0.65 + 0.95*z[17+product]; } // 9 products
    double pressure_sensitivity() const { return 1.5*z[26]; }
    double growth_speed() const { return 0.55 + 1.45*z[27]; }
    int terminal_day() const { return 22 + iround(7*z[28]); }
    double land_density() const { return 0.45 + 0.47*z[29]; }
    double hire_aggr() const { return 0.55 + 0.90*z[30]; }
    double diversify() const { return z[31]; }
};

struct Task {
    int prio=0, x=0, y=0;
    uint8_t op=OP_PASS, arg=0;
    int key=0;
};

// Near-shed first, then spill east after land expansion. These are only a
// deterministic placement convention; counts/priorities are searched.
static constexpr int ANIMAL_SLOTS[][2] = {
    {4,4},{3,4},{2,4},{1,4},{1,3},{2,3},{3,3},{4,3},{4,2},{3,2},{2,2},{1,2},
    {5,4},{6,4},{7,4},{8,4},{8,3},{7,3},{6,3},{5,3},{5,2},{6,2},{7,2},{8,2}
};
static constexpr int N_ANIMAL_SLOTS = sizeof(ANIMAL_SLOTS)/sizeof(ANIMAL_SLOTS[0]);
static constexpr int CROP_SLOTS[][2] = {
    {4,1},{3,1},{2,1},{1,1},{0,1},{4,0},{3,0},{2,0},{1,0},{0,0},{0,2},{0,3},{0,4},
    {5,1},{6,1},{7,1},{8,1},{9,1},{5,0},{6,0},{7,0},{8,0},{9,0},{9,2},{9,3},{9,4}
};
static constexpr int N_CROP_SLOTS = sizeof(CROP_SLOTS)/sizeof(CROP_SLOTS[0]);

inline bool unlocked(const Farm& f, int x, int y) { return f.tiles[y][x].kind != T_LOCKED; }
inline bool shed_adj(int x,int y) { return is_shed_adjacent(x,y,BOARD); }

void nearest_shed(int x, int y, int& tx, int& ty) {
    int pts[4][2]; shed_access_tiles(BOARD, pts);
    int best=999;
    tx=pts[0][0]; ty=pts[0][1];
    for (int i=0;i<4;++i) {
        int d=manhattan(x,y,pts[i][0],pts[i][1]);
        if (d<best) { best=d; tx=pts[i][0]; ty=pts[i][1]; }
    }
}

UnitAction move_toward(int x,int y,int tx,int ty) {
    UnitAction a;
    if (x<tx) a.op=OP_EAST;
    else if (x>tx) a.op=OP_WEST;
    else if (y<ty) a.op=OP_SOUTH;
    else if (y>ty) a.op=OP_NORTH;
    else a.op=OP_PASS;
    return a;
}

int carried(const Farm& f, int item) {
    int n=0; for(int u=0;u<f.n_units;++u) n += f.inv[u][item]; return n;
}
int live_animals(const Farm& f, int item) {
    int n=0;
    for(int y=0;y<BOARD;++y) for(int x=0;x<BOARD;++x) {
        const Tile& t=f.tiles[y][x]; if(t.has_animal && t.what==item) ++n;
    }
    return n;
}
int owned_animals(const Farm& f, int item) { return live_animals(f,item)+f.shed[item]+carried(f,item); }
int crop_count(const Farm& f,int crop) {
    int n=0; for(int y=0;y<BOARD;++y) for(int x=0;x<BOARD;++x) {
        const Tile& t=f.tiles[y][x]; if(t.kind==T_PLANT && t.what==crop) ++n;
    } return n;
}
int productive_assets(const Farm& f) {
    int n=0; for(int y=0;y<BOARD;++y) for(int x=0;x<BOARD;++x) {
        const Tile& t=f.tiles[y][x]; if(t.kind==T_PLANT || t.has_animal) ++n;
    } return n;
}
int occupied_unlocked(const Farm& f) {
    int n=0; for(int y=0;y<BOARD;++y) for(int x=0;x<BOARD;++x)
        if(f.tiles[y][x].kind!=T_LOCKED && f.tiles[y][x].kind!=T_EMPTY) ++n;
    return n;
}
int available_unlocked(const Farm& f) {
    int n=0; for(int y=0;y<BOARD;++y) for(int x=0;x<BOARD;++x)
        if(f.tiles[y][x].kind!=T_LOCKED) ++n; return n;
}

// Visible opponent productive pressure. No private inventory is inspected.
double opponent_pressure(const Farm& opp, int product) {
    double q=0.0;
    for(int y=0;y<BOARD;++y) for(int x=0;x<BOARD;++x) {
        const Tile& t=opp.tiles[y][x];
        if(t.kind==T_PLANT && t.what==product && product<N_CROPS) q += 0.8 + t.yield_units;
        if(t.has_animal) {
            const AnimalDef& ad=ANIMALS[t.what-GOOSE];
            if(ad.product==product) q += 1.2 + t.yield_units;
        }
    }
    return q;
}

int effective_target(int raw, double pressure, const Params& p) {
    if(raw<=0) return 0;
    double cut = p.diversify()*p.pressure_sensitivity()*std::min(0.45, pressure/(35.0+4.0*raw));
    return std::max(0, iround(raw*(1.0-cut)));
}

struct Controller {
    Params p;
    explicit Controller(const double* row):p(row){}

    Action act(const Sim& sim, int player) const {
        Action a; a.clear();
        const State& st=sim.st;
        const Farm& f=st.farms[player];
        const Farm& opp=st.farms[1-player];
        const int day=st.day, hour=st.hour;
        const int remaining=std::max(0, sim.cfg.episode_steps-1-st.step);
        const bool terminal = day>=p.terminal_day() || remaining<=24;

        // ----- strategic targets: continuous parameter vector -> current targets.
        double ramp=std::min(1.0, p.growth_speed()*(day+1)/10.0);
        int atarget[3] = {p.goose_max(),p.cow_max(),p.sheep_max()};
        for(int k=0;k<3;++k) {
            int item=GOOSE+k;
            int prod=ANIMALS[k].product;
            atarget[k]=effective_target(iround(atarget[k]*ramp),opponent_pressure(opp,prod),p);
            if(terminal) atarget[k]=live_animals(f,item);
        }
        int ctarget[5];
        for(int c=0;c<5;++c) {
            ctarget[c]=effective_target(iround(p.crop_max(c)*ramp),opponent_pressure(opp,c),p);
            if(c==WHEAT) ctarget[c]=std::max(ctarget[c], std::min(18, 2+owned_animals(f,GOOSE)+owned_animals(f,COW)+owned_animals(f,SHEEP)));
            if(terminal) ctarget[c]=crop_count(f,c);
        }

        // ----- market layer.
        double budget=std::max(0.0, f.money-p.reserve());
        auto add_order=[&](uint8_t op,uint8_t item,int n){
            if(a.n_orders>=sim.cfg.max_orders || n<=0) return false;
            Order o; o.op=op; o.item=item; o.n=n; a.orders[a.n_orders++]=o; return true;
        };
        auto add_simple=[&](uint8_t op){
            if(a.n_orders>=sim.cfg.max_orders) return false;
            Order o; o.op=op; o.n=1; a.orders[a.n_orders++]=o; return true;
        };

        // Liquidation / state-sensitive sales. Sell thresholds are factorized by product.
        for(int prod=0;prod<N_PRODUCTS;++prod) {
            int q=f.shed[prod]; if(q<=0) continue;
            double factor=p.sell_common()*p.sell_factor(prod);
            double pressure=opponent_pressure(opp,prod);
            bool sell = terminal || remaining<=48 || st.market.prices[prod] >= MARKET[prod].base*factor ||
                        (p.pressure_sensitivity()*pressure >= 8.0 && hour<=2);
            if(sell) add_order(M_SELL,prod,q);
        }
        if(!terminal) {
            // Survival wheat is allowed to spend inside the nominal reserve.
            int alive=live_animals(f,GOOSE)+live_animals(f,COW)+live_animals(f,SHEEP);
            int wheat=f.shed[WHEAT]+carried(f,WHEAT);
            int want=std::min(30, iround(alive*p.wheat_per_animal()));
            if(wheat<want) {
                int price=std::max(1,st.market.prices[WHEAT]);
                int afford=static_cast<int>(std::max(0.0,f.money-25.0)/price);
                add_order(M_BUY_PRODUCT,WHEAT,std::min(want-wheat,afford));
            }

            // Animals: at most a few per turn; all three species are independent heads.
            for(int k=0;k<3;++k) {
                int item=GOOSE+k, miss=std::max(0,atarget[k]-owned_animals(f,item));
                int cost=ANIMALS[k].cost;
                int buy=std::min(3,std::min(miss,static_cast<int>(budget/cost)));
                if(buy>0 && add_order(M_BUY_ANIMAL,item,buy)) budget-=buy*cost;
            }
            // Seeds for all five crops, not just a named plan's selected subset.
            for(int c=0;c<N_CROPS;++c) {
                int have=crop_count(f,c)+f.seeds[c];
                int miss=std::max(0,ctarget[c]-have);
                int cost=CROPS[c].seed;
                int buy=std::min(10,std::min(miss,static_cast<int>(budget/cost)));
                if(buy>0 && add_order(M_BUY_SEED,c,buy)) budget-=buy*cost;
            }

            // Labour only early in the day; HIRE is one market slot each.
            int work=productive_assets(f);
            int desired=std::min(p.hands(), std::max(2,iround((2.0+0.65*work)*p.hire_aggr())));
            if(hour<=2) {
                int h=f.hires_today;
                while(h<desired && a.n_orders<sim.cfg.max_orders) {
                    int cost=fib(h)*sim.cfg.hire_mult;
                    if(f.money < cost+25) break;
                    add_simple(M_HIRE); ++h;
                }
            }
            // Land only when actual density says capacity is binding.
            double density=occupied_unlocked(f)/static_cast<double>(std::max(1,available_unlocked(f)));
            if(f.n_quadrants<p.lands() && density>=p.land_density() && a.n_orders<sim.cfg.max_orders) {
                int idx=f.n_quadrants-1;
                int cost=(idx>=0 && idx<3)?LAND_PRICES[idx]:999999;
                if(f.money>=cost+p.reserve()*0.35) add_simple(M_BUY_LAND);
            }
        }

        // ----- mechanical task layer.
        std::vector<Task> tasks;
        tasks.reserve(256);
        auto push=[&](int pr,int x,int y,uint8_t op,uint8_t arg=0,int key=0){
            Task t; t.prio=pr;t.x=x;t.y=y;t.op=op;t.arg=arg;t.key=key;tasks.push_back(t);
        };

        int wheat_supply=f.shed[WHEAT]+carried(f,WHEAT);
        int fert_supply=f.shed[FERTILIZER]+carried(f,FERTILIZER);
        for(int y=0;y<BOARD;++y) for(int x=0;x<BOARD;++x) {
            const Tile& t=f.tiles[y][x];
            int key=(y*BOARD+x)*32;
            if(t.kind==T_WEED) { push(35,x,y,OP_DIG,0,key+1); continue; }
            if(t.kind==T_PLANT) {
                if(!t.watered_today) push((t.consecutive_dry>=1)?132:98,x,y,OP_WATER,0,key+2);
                if(t.yield_units>=p.harvest_trigger() || (remaining<=48 && t.yield_units>0))
                    push(terminal?115:72,x,y,OP_HARVEST,0,key+3);
                if(fert_supply>0 && t.fertilized_until_day<day && t.what!=WHEAT)
                    push(p.fert_prio(),x,y,OP_FERTILIZE,FERTILIZER,key+4);
            }
            if(t.has_animal) {
                if(!t.fed_today && wheat_supply>0)
                    push((t.consecutive_dry>=1)?145:p.feed_prio(),x,y,OP_FEED,WHEAT,key+5);
                if(t.fed_today && !t.cared_today) push(p.care_prio(),x,y,OP_CARE,0,key+6);
                if(t.fertilizer_available) push(80,x,y,OP_COLLECT_FERTILIZER,0,key+7);
                if(t.yield_units>=p.harvest_trigger() || (remaining<=48 && t.yield_units>0))
                    push(terminal?120:76,x,y,OP_HARVEST,0,key+8);
            }
        }

        // Animal structures / placement. Preserve every live animal; only free slots used.
        int slot_i=0;
        for(int k=0;k<3;++k) {
            int animal=GOOSE+k;
            int need=std::max(0,atarget[k]-live_animals(f,animal));
            while(need>0 && slot_i<N_ANIMAL_SLOTS) {
                int x=ANIMAL_SLOTS[slot_i][0],y=ANIMAL_SLOTS[slot_i][1]; ++slot_i;
                if(!unlocked(f,x,y)) continue;
                const Tile& t=f.tiles[y][x];
                if(t.has_animal) continue;
                TileKind want=(ANIMALS[k].structure==ST_COOP)?T_COOP:T_PASTURE;
                int key=(y*BOARD+x)*32;
                if(t.kind==T_EMPTY) push(62,x,y,want==T_COOP?OP_BUILD_COOP:OP_BUILD_PASTURE,0,key+9);
                else if(t.kind==want && !t.has_animal) push(64,x,y,OP_PLACE,animal,key+10);
                --need;
            }
        }

        // Crop setup: factorized targets, resource-capped so atomic PLANT cannot self-cancel.
        int seeds_left[N_CROPS]; for(int c=0;c<N_CROPS;++c) seeds_left[c]=f.seeds[c];
        int cs=0;
        // Put high-value crops first, wheat fills the remainder.
        static const int order[5]={MELON,STRAWBERRY,TOMATO,CARROT,WHEAT};
        for(int oi=0;oi<5;++oi) {
            int c=order[oi]; int need=std::max(0,ctarget[c]-crop_count(f,c));
            for(int n=0;n<need && cs<N_CROP_SLOTS && seeds_left[c]>0;) {
                int x=CROP_SLOTS[cs][0],y=CROP_SLOTS[cs][1]; ++cs;
                if(!unlocked(f,x,y) || f.tiles[y][x].kind!=T_EMPTY) continue;
                push(58,x,y,OP_PLANT,c,(y*BOARD+x)*32+11); --seeds_left[c]; ++n;
            }
        }

        std::sort(tasks.begin(),tasks.end(),[](const Task& A,const Task& B){
            if(A.prio!=B.prio) return A.prio>B.prio;
            return A.key<B.key;
        });
        std::vector<uint8_t> claimed(tasks.size(),0);
        a.n_units=f.n_units;
        int reserved_shed[N_ITEMS]={0};

        for(int u=0;u<f.n_units;++u) {
            UnitAction ua; ua.op=OP_PASS;
            int x=f.pos_x[u],y=f.pos_y[u];

            // If carrying purchased animal, finish placement before doing anything else.
            bool committed=false;
            for(int animal=GOOSE;animal<=SHEEP && !committed;++animal) if(f.inv[u][animal]>0) {
                int k=animal-GOOSE, bx=-1,by=-1,best=999;
                TileKind want=(ANIMALS[k].structure==ST_COOP)?T_COOP:T_PASTURE;
                for(int yy=0;yy<BOARD;++yy) for(int xx=0;xx<BOARD;++xx) {
                    const Tile& t=f.tiles[yy][xx]; if(t.kind==want && !t.has_animal) {
                        int d=manhattan(x,y,xx,yy); if(d<best){best=d;bx=xx;by=yy;}
                    }
                }
                if(bx>=0) {
                    if(x==bx&&y==by){ua.op=OP_PLACE;ua.arg=animal;ua.n=1;}
                    else ua=move_toward(x,y,bx,by);
                    committed=true;
                }
            }
            if(committed){a.units[u]=ua;continue;}

            // Carrying ordinary output -> shed; carrying wheat/fertilizer may be consumed by a task below.
            int carried_output=0;
            for(int it=CARROT;it<=WOOL;++it) if(it!=FERTILIZER) carried_output+=f.inv[u][it];
            if(carried_output>0 && f.inv[u][WHEAT]==0) {
                int sx,sy; nearest_shed(x,y,sx,sy);
                if(shed_adj(x,y)){ua.op=OP_DROP;} else ua=move_toward(x,y,sx,sy);
                a.units[u]=ua; continue;
            }

            // Pick best unclaimed reachable task, with required-item logistics folded in.
            int chosen=-1; double bestscore=-1e18;
            for(size_t ti=0;ti<tasks.size();++ti) if(!claimed[ti]) {
                const Task& t=tasks[ti];
                bool need_item=(t.op==OP_FEED||t.op==OP_FERTILIZE||t.op==OP_PLACE);
                int req=t.arg;
                int dist=manhattan(x,y,t.x,t.y);
                if(need_item && f.inv[u][req]<=0) {
                    int avail=f.shed[req]-reserved_shed[req];
                    if(avail<=0) continue;
                    int sx,sy;nearest_shed(x,y,sx,sy); dist=manhattan(x,y,sx,sy)+manhattan(sx,sy,t.x,t.y)+1;
                }
                double score=t.prio*100.0-dist;
                if(score>bestscore){bestscore=score;chosen=static_cast<int>(ti);}
            }
            if(chosen>=0) {
                Task t=tasks[chosen]; claimed[chosen]=1;
                bool need_item=(t.op==OP_FEED||t.op==OP_FERTILIZE||t.op==OP_PLACE);
                int req=t.arg;
                if(need_item && f.inv[u][req]<=0) {
                    int sx,sy;nearest_shed(x,y,sx,sy);
                    if(shed_adj(x,y)) {
                        int avail=std::max(0,f.shed[req]-reserved_shed[req]);
                        int take=std::min(req==WHEAT?3:1,avail);
                        if(take>0){ua.op=OP_PICKUP;ua.arg=req;ua.n=take;reserved_shed[req]+=take;}
                    } else ua=move_toward(x,y,sx,sy);
                } else if(x==t.x&&y==t.y) {
                    ua.op=t.op; ua.arg=t.arg; ua.n=1;
                } else ua=move_toward(x,y,t.x,t.y);
            } else if(f.inv[u][WHEAT]>0 || f.inv[u][FERTILIZER]>0) {
                int sx,sy;nearest_shed(x,y,sx,sy);
                if(shed_adj(x,y)) ua.op=OP_DROP; else ua=move_toward(x,y,sx,sy);
            }
            a.units[u]=ua;
        }
        return a;
    }
};

struct EvalRow {
    double mean_margin=0, win_rate=0, tie_rate=0, mean_own=0, mean_opp=0;
    double worst_margin=std::numeric_limits<double>::infinity();
    double silent_loss=0, dead_actions=0, hand_pass=0, animals_escaped=0, plants_dry=0;
    int games=0;
};

void add_telemetry(const Farm& f, EvalRow& r) {
    int more_dead=f.tel_move_dead+f.tel_locked_dead+f.tel_pickup_dead+f.tel_drop_dead+
        f.tel_place_dead+f.tel_build_dead+f.tel_dig_dead+f.tel_fertilize_dead+
        f.tel_collect_dead+f.tel_care_dead;
    r.dead_actions += f.tel_feed_no_wheat+f.tel_feed_no_animal+f.tel_feed_redundant+
        f.tel_water_dead+f.tel_harvest_dead+f.tel_plant_dead+more_dead;
    r.silent_loss += f.tel_escape_capital+f.tel_dry_seed_cost;
    r.hand_pass += f.tel_hand_pass_turns;
    r.animals_escaped += f.tel_animals_escaped;
    r.plants_dry += f.tel_plants_dry;
}

std::pair<double,double> play_one(const Params& pa,const Params& pb,uint64_t seed,
                                  int cand_seat, EvalRow* tel) {
    Config c; c.seed=seed; c.episode_steps=720; Sim sim(c);
    Controller ca(pa.z.data()), cb(pb.z.data());
    while(!sim.st.done) {
        Action a0 = cand_seat==0 ? ca.act(sim,0) : cb.act(sim,0);
        Action a1 = cand_seat==1 ? ca.act(sim,1) : cb.act(sim,1);
        sim.step(a0,a1);
    }
    double own=sim.reward(cand_seat), other=sim.reward(1-cand_seat);
    if(tel) add_telemetry(sim.st.farms[cand_seat],*tel);
    return {own,other};
}

void parallel_for(size_t n,int threads,const std::function<void(size_t)>& fn) {
    if(n==0)return; unsigned hw=std::thread::hardware_concurrency();
    int nt=threads>0?threads:static_cast<int>(hw?hw:1u); nt=std::max(1,std::min<int>(nt,n));
    if(nt==1){for(size_t i=0;i<n;++i)fn(i);return;}
    std::atomic<size_t> next{0}; std::vector<std::thread> pool; pool.reserve(nt);
    for(int t=0;t<nt;++t)pool.emplace_back([&]{for(;;){size_t i=next.fetch_add(1);if(i>=n)return;fn(i);}});
    for(auto& th:pool)th.join();
}

} // namespace

PYBIND11_MODULE(kagteacher,m) {
    m.doc()="Kculture native parametric adaptive search teacher over exact Kaggriculture 1.32.7";
    m.def("evaluate",[](py::array_t<double,py::array::c_style|py::array::forcecast> candidates,
                         py::array_t<double,py::array::c_style|py::array::forcecast> opponents,
                         const std::vector<uint64_t>& seeds,int threads) {
        auto cb=candidates.request(), ob=opponents.request();
        if(cb.ndim!=2||ob.ndim!=2||cb.shape[1]!=P||ob.shape[1]!=P) throw std::invalid_argument("params must be [N,32] and [M,32]");
        size_t N=cb.shape[0], M=ob.shape[0]; if(M==0||seeds.empty()) throw std::invalid_argument("need opponents and seeds");
        const double* cp=static_cast<const double*>(cb.ptr); const double* op=static_cast<const double*>(ob.ptr);
        std::vector<EvalRow> rows(N);
        auto t0=std::chrono::steady_clock::now();
        {
            py::gil_scoped_release rel;
            parallel_for(N,threads,[&](size_t i){
                Params pc(cp+i*P); EvalRow r;
                for(size_t j=0;j<M;++j){ Params po(op+j*P);
                    for(uint64_t seed:seeds) for(int seat=0;seat<2;++seat){
                        auto [own,other]=play_one(pc,po,seed,seat,&r); double margin=own-other;
                        r.mean_margin+=margin; r.mean_own+=own; r.mean_opp+=other; r.worst_margin=std::min(r.worst_margin,margin); ++r.games;
                        if(margin>0)r.win_rate+=1; else if(margin==0)r.tie_rate+=1;
                    }
                }
                double g=std::max(1,r.games); r.mean_margin/=g;r.mean_own/=g;r.mean_opp/=g;r.win_rate/=g;r.tie_rate/=g;
                r.silent_loss/=g;r.dead_actions/=g;r.hand_pass/=g;r.animals_escaped/=g;r.plants_dry/=g; rows[i]=r;
            });
        }
        double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
        auto arr=[&](auto getter){py::array_t<double> a(N);double* p=a.mutable_data();for(size_t i=0;i<N;++i)p[i]=getter(rows[i]);return a;};
        py::dict d;
        d["mean_margin"]=arr([](const EvalRow&r){return r.mean_margin;});
        d["win_rate"]=arr([](const EvalRow&r){return r.win_rate;});
        d["tie_rate"]=arr([](const EvalRow&r){return r.tie_rate;});
        d["mean_own_bank"]=arr([](const EvalRow&r){return r.mean_own;});
        d["mean_opp_bank"]=arr([](const EvalRow&r){return r.mean_opp;});
        d["worst_margin"]=arr([](const EvalRow&r){return r.worst_margin;});
        d["silent_loss_coins"]=arr([](const EvalRow&r){return r.silent_loss;});
        d["dead_actions"]=arr([](const EvalRow&r){return r.dead_actions;});
        d["hand_pass_turns"]=arr([](const EvalRow&r){return r.hand_pass;});
        d["animals_escaped"]=arr([](const EvalRow&r){return r.animals_escaped;});
        d["plants_dry"]=arr([](const EvalRow&r){return r.plants_dry;});
        d["seconds"]=sec; d["episodes_per_second"]=(N*M*seeds.size()*2)/std::max(1e-9,sec);
        d["games_per_candidate"]=static_cast<int>(M*seeds.size()*2);
        return d;
    },py::arg("candidates"),py::arg("opponents"),py::arg("seeds"),py::arg("threads")=0);
    m.attr("PARAM_WIDTH")=P;
    m.attr("ENGINE_VERSION")="1.32.7";
    m.attr("SCHEMA")="kculture-native-teacher-v0";
}
