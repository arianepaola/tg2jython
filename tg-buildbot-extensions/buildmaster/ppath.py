#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""This module contains functions to create PYTHONPATHs """


__program__   = "ppath.py"
__author__    = "Steven Mohr"
__version__   = "0.1"
__revision__  = "$Rev:$"
__date__      = "$Date:$"
__copyright__ = "MIT license"

import re
import os
def splitppath(ppath):
    """Splits the path at the colon and return the parts as a tuple"""
    temp = re.split(":",ppath,1)
    return temp

def modifyppath(ppath,folder):
    """Extends PYTHONPATH with folder"""
    temp2 = splitppath(ppath)
    temp = os.path.join(folder,temp2[0]) +":"+os.path.join(folder,temp2[1])
    return temp