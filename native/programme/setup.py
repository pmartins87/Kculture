from pathlib import Path
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SIM = ROOT / "external" / "kaggriculture-cppsim" / "sim"

if not (SIM / "sim.hpp").is_file():
    raise RuntimeError(f"missing pinned kagsim sim.hpp at {SIM}")

ext = Pybind11Extension(
    "kagprog",
    [str(HERE / "kagprog.cpp")],
    include_dirs=[str(SIM)],
    cxx_std=17,
    extra_compile_args=["-O3", "-DNDEBUG", "-include", "functional", "-include", "stdexcept"],
)

setup(
    name="kagprog",
    version="0.1.0",
    ext_modules=[ext],
    cmdclass={"build_ext": build_ext},
)
