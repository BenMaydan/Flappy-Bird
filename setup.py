from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("cython_logic", ["cython_logic.pyx"])]

setup(
      name='Flappy Bird Clone',
      cmdclass={'build_ext': build_ext},
      ext_modules=ext_modules
)
