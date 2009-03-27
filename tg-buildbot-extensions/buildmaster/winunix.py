__program__   = "winunix.py"
__author__    = "Steven Mohr"
__version__   = "0.1"
__revision__  = "$Rev:$"
__date__      = "$Date:$"
__copyright__ = "MIT license"

"""Contains workarounds for interoperability"""
import os

def correctseperator(arg):
    if os.sep =='\\':
            arg = arg.replace('/','\\')
    return arg

    
def correctpathdepth(workdir):
    """returns the prefix for the path. It analyses the workdir string and creates an proper number of .. for the path"""
    depth = workdir.count(os.sep)
    prefix = ""
    for i in range(depth):
        prefix= ".." + os.sep + prefix
    
    return prefix