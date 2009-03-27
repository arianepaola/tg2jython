#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" """


__program__   = "updateSetupCfg.py"
__author__    = "Steven Mohr"
__version__   = "0.1"
__revision__  = "$Rev:$"
__date__      = "$Date:$"
__copyright__ = "MIT license"

import sys
import os 

file = open("setup.cfg","a")
path =''
if len(sys.argv) > 1:
	path = str(sys.argv[1])
file.write("\n[install]\n")
file.write("install_lib="+path+"lib\n")
file.write("install_data=" +path+"lib\n")
file.write("install_scripts =" +path+"bin\n")
file.close()