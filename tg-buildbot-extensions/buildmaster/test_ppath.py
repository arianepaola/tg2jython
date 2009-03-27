#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Some function to test ppath.py"""

__program__   = "test_ppath.py"
__author__    = "Steven Mohr"
__version__   = "0.1"
__revision__  = "$Rev:$"
__date__      = "$Date:$"
__copyright__ = "MIT license"

from ppath import *
import unittest

def test_split():
	"tests splitPPath"
	assert splitppath("bin:lib") == ["bin","lib"]
	assert splitppath("../bin:../lib") == ["../bin","../lib"]

def test_modify():
	"tests modifyPPath"
	assert modifyppath("bin:lib","..") == "../bin:../lib"