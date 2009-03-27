__program__   = "winunix.py"
__author__    = "Steven Mohr"
__version__   = "0.1"
__revision__  = "$Rev:$"
__date__      = "$Date:$"
__copyright__ = "MIT license"

"""Contains workarounds for interoperability"""
import winunix
import unittest

def test_correctpathdepth():
    
    test_pairs = [("build\\bli","..\\"),("build\\bli\\bla","..\\..\\"),("build","")]

    for element in test_pairs:
        a = winunix.correctpathdepth(element[0])
        print "Input: %s  Output: %s Erwarteter Output: %s" % (element[0], a, element[1])
        assert a == element[1] 