from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

ROOT = Path(__file__).resolve().parents[2]
SIM_INCLUDE = ROOT / "external" / "kaggriculture-cppsim" / "sim"

if not (SIM_INCLUDE / "sim.hpp").exists():
    raise SystemExit(
        f"missing pinned kagsim checkout at {SIM_INCLUDE}; "
        "clone destbreso/kaggriculture-cppsim first"
    )

setup(
    name="kculture-kagvec",
    version="0.0.1",
    ext_modules=[
        Pybind11Extension(
            "kagvec",
            [str(Path(__file__).with_name("kagvec.cpp"))],
            include_dirs=[str(SIM_INCLUDE)],
            cxx_std=17,
            # `-include` keeps the prototype source minimal while making its
            # standard-library dependencies explicit across GCC toolchains.
            extra_compile_args=[
                "-O3", "-DNDEBUG",
                "-include", "functional",
                "-include", "stdexcept",
            ],
        )
    ],
    cmdclass={"build_ext": build_ext},
)
