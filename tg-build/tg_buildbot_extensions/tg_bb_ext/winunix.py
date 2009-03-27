"""Contains workarounds for interoperability"""

__program__   = "winunix.py"
__author__    = "Steven Mohr"
__version__   = "0.1"
__revision__  = "$Rev:$"
__date__      = "$Date:$"
__copyright__ = "MIT license"


import os

def correctseperator(path):
    """ This function corrects the seperator on WinOS.
    :param path: path that should be corrected
    :type path: string"""
    if os.sep == '\\':
        path = path.replace('/','\\')
    return path

def correctpathdepth(workdir):
    """It analyses the workdir
     string and creates an proper number of .. for the path
     :param workdir: workdir of the step
     :type workdir: string
     :return: prefix for the path
     :rtype: string"""
    depth = workdir.count(os.sep)
    prefix = ""
    for i in range(depth):
        prefix = ".." + os.sep + prefix
    
    return prefix

def createpath(workdir):
    """createpath constructs the PATH variable with the bin
    respectively scripts directory included
    :param workdir: workdir of the step
    :type workdir: string
    :return: string to used as PATH
    :rtype: string"""
    if os.name in ['nt', 'ce']:
        return correctpathdepth(workdir) + 'scripts' +\
        os.path.pathsep + os.getenv("PATH")
    else:
        return correctpathdepth(workdir) + 'bin' +\
        os.path.pathsep + os.getenv("PATH")