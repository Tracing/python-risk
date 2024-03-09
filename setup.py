from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize(["engine.pyx", "cards.pyx", "RiskMap.pyx", "helper_functions.pyx"], annotate=True)
)