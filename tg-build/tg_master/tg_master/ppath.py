#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""This module contains functions to create and modify PYTHONPATHs """

__program__   = "ppath.py"
__author__    = "Steven Mohr"
__version__   = "0.1"
__revision__  = "$Rev:$"
__date__      = "$Date:$"
__copyright__ = "MIT license"

import os
def splitppath(ppath):
    """
    Splits the input at the colon and returns the parts
    
    :param ppath: pythonpath that should be splitted
    :type ppath: string
    :return: parts of the pythonpath
    :rtype: list with two elements: bin/script directory and
      lib directory
    
    **Usage**
    
    >>> splitppath("bin:lib")
    ['bin', 'lib']
    
    >>> splitppath("../bin:../lib")
    ['../bin', '../lib']
    """
    
    temp = ppath.rsplit(":", 1)
    return temp

def modifyppath(ppath, folder):
    """
    Joins the pythonpath and the folder.
    
    :param ppath: pythonpath that should be extended
    :type ppath: string
    :param folder: folder that extends the python path
    :type folder: string
    :return: joined pythonpath
    :rtype: string
    
    **Usage**
    
    >>> modifyppath("bin:lib", "..")
    '../bin:../lib'
    
    """
    temp2 = splitppath(ppath)
    temp = os.path.join(folder, temp2[0]) + ":" +\
     os.path.join(folder, temp2[1])
    return temp