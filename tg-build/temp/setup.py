#!/usr/bin/env python
#
# Setup script for the subprocess module
#
# Usage: python setup.py install
#

from distutils.core import setup, Extension
import sys

if sys.platform == "win32":
    ext_modules = [Extension("_subprocess", ["_subprocess.c"])]
else:
    ext_modules = []

setup(
    name="subprocess",
    version="0.1",
    author="Peter Astrand",
    author_email="astrand@lysator.liu.se",
    description="subprocess module",
    py_modules = ["subprocess"],
    ext_modules = ext_modules
    )
