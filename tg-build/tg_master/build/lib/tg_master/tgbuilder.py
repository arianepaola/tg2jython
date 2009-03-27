""" 
This module contains functions to automate creation of BuildFactories and
other helpful functions to use in master.cfg
"""

from buildbot.process import factory
from buildbot.steps.shell import ShellCommand
from buildbot.steps.transfer import FileDownload
from buildbot.steps import source

from ppath import modifyppath
from buildbot.buildslave import BuildSlave
from tg_mbuildsteps import * 

#################### TG 1.0 builder ###################################
def tg10builder(quick, pythonpath = "bin:lib"):
    """tg10builder returns a BuildFactory which downloads TG1.0 from SVN, 
       installs all dependencies, runs the core tests, creates all posible  
       quickstart projects, runs the tests for all of this projects and  
       builds the egg.
         
       :parameter pythonpath:  This is the path, which is used for all
         python scripts. pythonpath must fit the pattern: "binDir:libDir". 
       :type pythonpath: string 
       :param quick: Sets quick build mode 
       :type quick: boolean""" 

    ftg1 = factory.BuildFactory()
    
    if quick:
        ftg1.addStep(source.SVN(mode='update',
                                svnurl="http://svn.turbogears.org/"\
                                "branches/1.0"))
    else:
        ftg1.addStep(source.SVN(mode='clobber',
                                svnurl="http://svn.turbogears.org/"\
                                "branches/1.0"))
        ftg1.addStep(FileDownload, mastersrc="autobuild_quickstarts.py",
	    slavedest="autobuild_quickstarts.py")
        ftg1.addStep(FileDownload, mastersrc="upload_script.py",
	    slavedest="upload_script.py")
    
    ftg1.addStep(VirtualEnv, env={'PYTHONPATH':pythonpath}, haltOnFailure=True)
    ftg1.addStep(InterOSShellCommand, command=["cp", "python2.3", "python"],
                 description="Rename python23", workdir="build/bin",
                 flunkOnFailure=False)

    if quick:
        ftg1.addStep(EasyInstall, package=["cherrypy"],
                     env={'PYTHONPATH':pythonpath}, haltOnFailure=True)    
    else:
        ftg1.addStep(Python, script="externals.py", workdir="build/thirdparty",
                env={'PYTHONPATH':pythonpath}, haltOnFailure=True)
        ftg1.addStep(RunSetup, description="Installing TG1",
                env={'PYTHONPATH':pythonpath}, haltOnFailure=True)
        ftg1.addStep(EasyInstall, package=["SQLAlchemy", "SQLObject", "Genshi",
                "gsquickstart", "docutils"], env={'PYTHONPATH':pythonpath},
                haltOnFailure=True)
        
    ftg1.addStep(EasyInstall, package=["nose"],
                 env={'PYTHONPATH':pythonpath}, haltOnFailure=True)

    ftg1.addStep(Nose, verbose=True, testdir="turbogears/tests",
                 description="Running nosetest TG",
                 env={'PYTHONPATH':pythonpath}, haltOnFailure=True)
    
    if quick == False:
        ftg1.addStep(Python, script="autobuild_quickstarts.py",
                     description="Creating quickstart projects",
                     env={'PYTHONPATH':pythonpath})
        
        ftg1.addStep(Nose, description="Running nosetest Quickstart",
                 env={'PYTHONPATH':pythonpath}, testdir="build")
        
    ftg1.addStep(BuildEgg, description="Building TG1 egg",
                 env={'PYTHONPATH':pythonpath}, haltOnFailure=True)
    ftg1.addStep(EasyInstall, env={'PYTHONPATH':pythonpath}, 
                 localinstall = True, haltOnFailure = True)
    
    if quick == False:
        ftg1.addStep(UploadEgg, env={'PYTHONPATH':pythonpath},
                     package=["TurboGears 1"])
    return ftg1


##################### TG 1.1 -Builder ######################

def tg11builder(quick, pythonpath = "bin:lib"):
    """
    tg11builder returns a BuildFactory which downloads TG1.1 from SVN, 
    installs all dependencies,runs the core tests, creates all posible 
    quickstart projects, runs the tests for all of this projects and builds 
    the egg.
         
    :parameter pythonpath:  This is the path, which is used for all python 
      scripts. pythonpath must fit the pattern: "binDir:libDir". 
    :type pythonpath: string 
    :param quick: Sets quick build mode 
    :type quick: boolean
       
    """ 
    ftg11 = factory.BuildFactory()

    if quick:
        ftg11.addStep(source.SVN(mode='update',
                      svnurl='http://svn.turbogears.org/branches/1.1'))
        ftg11.addStep(VirtualEnv, env={'PYTHONPATH':pythonpath},
                      haltOnFailure=True)
        ftg11.addStep(EasyInstall, package=["configobj", "SQLAlchemy", 
                                            "webtest", "sqlobject",
                                            "formencode", "mochikit",
                                            "decoratortools", 
                                            "peak-rules", "simplejson", 
                                            "genshi", "elixir","paste",
                                            "pastescript"])
    else:
        ftg11.addStep(source.SVN(mode='clobber',
                      svnurl='http://svn.turbogears.org/branches/1.1'))
        ftg11.addStep(FileDownload, mastersrc="autobuild_quickstarts.py",
                      slavedest="autobuild_quickstarts.py")
        ftg11.addStep(FileDownload, mastersrc="upload_script.py",
                      slavedest="upload_script.py")
        ftg11.addStep(VirtualEnv, env={'PYTHONPATH':pythonpath},
                      haltOnFailure=True)
        
    ftg11.addStep(InterOSShellCommand, command=["cp", "python2.3", "python"],
                  description="Rename python23",
                  workdir="build/bin", flunkOnFailure=False)
    
    if not quick:
        ftg11.addStep(EasyInstall, package=["SQLAlchemy", "SQLObject",
                      "Genshi", "gsquickstart", "docutils"],
                      description="Installing Dependencies",
                      env={"PYTHONPATH":pythonpath}, haltOnFailure=True)
        
        ftg11.addStep(Python, script="externals.py",
                      description="Running externals.py",
                      workdir="build/thirdparty", 
                      env={'PYTHONPATH':pythonpath},
                      haltOnFailure=True)
        
    ftg11.addStep(RunSetup, description="Installing TG11",
                  env={'PYTHONPATH':pythonpath}, haltOnFailure=True)

    ftg11.addStep(EasyInstall, package=["nose","webtest"],
                  description="installing nose + webtest",
                  env={'PYTHONPATH':pythonpath}, haltOnFailure=True)
    ftg11.addStep(Nose, testdir="turbogears/tests", verbose=True,
                  description="Running nosetest TG", 
                  env={'PYTHONPATH':pythonpath}, haltOnFailure=True)
    
    if not quick:
        ftg11.addStep(Python, script="autobuild_quickstarts.py",
                      description="Creating quickstart projects",
                      env={'PYTHONPATH':pythonpath}, haltOnFailure=True)
        ftg11.addStep(Nose, description="Running nosetest Quickstart",
                      env={'PYTHONPATH':pythonpath})

    ftg11.addStep(BuildEgg, description="Building TG11 egg",
                  env={'PYTHONPATH':pythonpath}, haltOnFailure=True)
    ftg11.addStep(EasyInstall, env={'PYTHONPATH':pythonpath}, 
                  localinstall = True, haltOnFailure = True)
    
    if quick == False:
        ftg11.addStep(UploadEgg, env={'PYTHONPATH':pythonpath}, 
                      package=["TurboGears 1.1"])
    return ftg11

######################### TG 2 -Builder ########################
def tg2builder(quick, pythonpath = "bin:lib"):
    """
    tg2builder returns a BuildFactory which downloads TG2 from SVN, 
    downloads pylons from mercurial, installs all dependencies, 
    runs the core tests, creates all posible quickstart projects,runs 
    the tests for all of this projects and builds the egg.
          
    :parameter pythonpath:  This is the path, which is used for all  
      python scripts. pythonpath must fit the pattern: "binDir:libDir". 
    :type pythonpath: string 
    :param quick: Sets quick build mode 
    :type quick: boolean
    """
    
    ftg2 = factory.BuildFactory()
    if quick:
        update_mode = 'update'
    else:
        update_mode = 'clobber'
	
    ftg2.addStep(source.Mercurial(repourl="http://pylonshq.com/hg/pylons-dev",
                                  alwaysUseLatest = True, mode=update_mode,
                                  workdir="build/pylons"), haltOnFailure=True)
    ftg2.addStep(source.SVN(mode=update_mode,
                            svnurl="http://svn.turbogears.org/" \
                            "projects/tg.devtools/trunk",
                            alwaysUseLatest = True, 
                            workdir='build/tgdev'),haltOnFailure=True)
    
    ftg2.addStep(source.SVN(mode=update_mode,
                            svnurl='http://svn.turbogears.org/trunk',
                            workdir='build/tg2', haltOnFailure = False))
    ftg2.addStep(source.SVN(mode=update_mode,
                            svnurl="http://svn.turbogears.org/projects/"\
                            "tgrepozewho/trunk", workdir='build/tgreoz',
                            alwaysUseLatest = True), haltOnFailure=True)
    
    if not quick:
        ftg2.addStep(source.Mercurial(
                                      repourl="https://www.knowledgetap.com"\
                                      "/hg/webhelpers",mode='clobber',
                                      workdir="build/webhelpers"),
                                      haltOnFailure=True)
        ftg2.addStep(FileDownload, mastersrc="upload_script.py",
                     slavedest="upload_script.py")
        ftg2.addStep(FileDownload, mastersrc="autobuild_quickstarts.py",
                     slavedest="autobuild_quickstarts.py")
    
    ftg2.addStep(VirtualEnv, env={'PYTHONPATH':pythonpath}, haltOnFailure=True)

    ftg2.addStep(EasyInstall, package=["nose"], description="installing nose",
                 env={'PYTHONPATH':pythonpath}, haltOnFailure=True)

    ftg2.addStep(EasyInstall, package=["paver"], description="Installing paver",
                 env={'PYTHONPATH':pythonpath})
    if quick == False:
        ftg2.addStep(EasyInstall, URL="http://turbogears.org/download/",
                     package=["RuleDispatch", "PyProtocols"],
                     description="Installing RuleDispatch + Pyprotocols",
                     env={'PYTHONPATH':pythonpath})

    newppath = modifyppath(pythonpath, "..")

    ftg2.addStep(RunSetup, devmode=True, description="Installing webhelpers",
                 env={'PYTHONPATH':newppath}, workdir="build/webhelpers")
    ftg2.addStep(RunSetup, devmode=True, description="Installing pylons",
                 env={'PYTHONPATH':newppath}, workdir="build/pylons",
                 haltOnFailure=True)
    
    ftg2.addStep(RunSetup, devmode=True, description="Installing tgreozewho",
                 env={'PYTHONPATH':newppath}, workdir="build/tgreoz")
    ftg2.addStep(Paver, description="Installing tg2", mode='develop',
                 env={'PYTHONPATH':newppath}, workdir="build/tg2",
                 haltOnFailure=True)
    ftg2.addStep(RunSetup, devmode=True, description="Installing tgdev",
                 env={'PYTHONPATH':newppath}, workdir="build/tgdev")
    
    ftg2.addStep(Nose, testdir="tg2/tg", verbose=True, haltOnFailure=True)
    ftg2.addStep(Nose, testdir="tgdev/devtools", verbose=True)
    ftg2.addStep(Nose, testdir="tgreoz/tgrepozewho", verbose=True)
    
    if quick == False:
        ftg2.addStep(Python, script="autobuild_quickstarts.py",
                     script_args=["TG2"], env={'PYTHONPATH':pythonpath},
                     description="Creating quickstart projects",
                     workdir="build")
        ftg2.addStep(Nose, description="Running nosetest Quickstart",
                     env={'PYTHONPATH':pythonpath})
        
    ftg2.addStep(Paver, mode="bdist_egg", description="Building TG2 egg",
                 env={'PYTHONPATH':pythonpath}, haltOnFailure=True)
    ftg2.addStep(EasyInstall, env={'PYTHONPATH':pythonpath}, 
                 localinstall = True, haltOnFailure = True)
    if quick == False:
        ftg2.addStep(UploadEgg, env={'PYTHONPATH':pythonpath},
                     package=["TurboGears 2"])
    return ftg2

def dependencybuildersvn(svn_url, pythonpath, name, dependencyfromtg=None):
    """ 
    dependencybuildersvn creates a build factory which does a 
    checkout from svnURL, downloads the dependencies specified 
    in DependencyFromTG from the TurboGears server,
    runs setup.py and builds the egg."""
    
    fdb = factory.BuildFactory()
    fdb.addStep(source.SVN(svnurl=svn_url, mode='clobber'))
    fdb.addStep(FileDownload, mastersrc="upload_script.py",
              slavedest="upload_script.py")
    fdb.addStep(VirtualEnv, env={'PYTHONPATH':pythonpath}, haltOnFailure=True)
    fdb.addStep(EasyInstall, package=["nose"], env={'PYTHONPATH':pythonpath},
              haltOnFailure=True)
    
    if dependencyfromtg is not None  :
        fdb.addStep(EasyInstall, URL="http://turbogears.org/download/",
                  description="Installing Dependencies",
                  package=dependencyfromtg, env={'PYTHONPATH':pythonpath})
    fdb.addStep(RunSetup, description="Installing " + name,
                env={'PYTHONPATH':pythonpath})
    fdb.addStep(Python, script="setup.py", script_args=["test"],
              description="Testing " + name, env={'PYTHONPATH':pythonpath},
              workdir="build", haltOnFailure=True)
    fdb.addStep(BuildEgg, env={'PYTHONPATH':pythonpath}, haltOnFailure=True)
    fdb.addStep(EasyInstall, env={'PYTHONPATH':pythonpath}, 
              localinstall = True, haltOnFailure = True)
    fdb.addStep(UploadEgg, env={'PYTHONPATH':pythonpath}, package=[name])
    return fdb

def dependencybuilderee(name, pythonpath = "bin:lib"):
    """dependencybuilderee creates a build factory which downloads the
     source of the dependency via easy_install and builds the egg."""
    fdb = factory.BuildFactory()
    fdb.addStep(CleanDir)
    fdb.addStep(FileDownload, mastersrc="upload_script.py",
              slavedest="upload_script.py")
    fdb.addStep(VirtualEnv, env={'PYTHONPATH':pythonpath}, haltOnFailure=True)
    fdb.addStep(EasyInstall, package=["Nose"])
    fdb.addStep(BuildEggEE, package=name[0], env={'PYTHONPATH':pythonpath})
    fdb.addStep(EasyInstall, env={'PYTHONPATH':pythonpath},
              localinstall = True, haltOnFailure = True)
    fdb.addStep(UploadEgg, env={'PYTHONPATH':pythonpath}, package=name)
    return fdb

def tg_ng_setupbuilder():
    """
    Tests next generation install scipt
    """
    fng = factory.BuildFactory()
    fng.addStep(CleanDir)
    fng.addStep(FileDownload, mastersrc="create-tgsetupng.py",
              slavedest="create-tgsetupng.py")
    fng.addStep(Python, script="create-tgsetupng.py", haltOnFailure=True)
    fng.addStep(Python, script="tgsetupng.py",
              script_args=["tg"], haltOnFailure=True)
    return fng

def doc_builder(**kwargs):
    """
    Creates documentation of a project. doc_builder takes an package name or
    an SVN repository as a source.
    
    :keyword framework: specifies the framework to use: sphinx or epydoc
    :type framework: string
    :keyword doc_dir: path to the files that should be documentated
    :type doc_dir: string
    :keyword package: Use this package as source 
      (DocBuilder downloads it from pypi.python.org)
    :type package: string
    :keyword svnurl: Use this repository as source
    :type svnurl: string
    :keyword needed_conf_file: path to a needed config file 
      that has to be downloaded from the build master
    :type needed_conf_file: string
    """
    fdoc = factory.BuildFactory()
    
    if 'framework' not in kwargs: 
        kwargs['framework'] = 'epydoc'
        
    if 'doc_dir' not in kwargs:
        kwargs['doc_dir'] = '' 
    
    if 'package' in kwargs: 
        fdoc.addStep(CleanDir) 
        fdoc.addStep(DownloadSourceEE, package=kwargs['package']) 
    else: 
        fdoc.addStep(source.SVN, svnurl=kwargs['svnurl'], mode='clobber')
        
    if 'needed_conf_file' in kwargs: 
        fdoc.addStep(FileDownload, mastersrc=kwargs['needed_conf_file'],
                  slavedest=kwargs['needed_conf_file'])
        if kwargs['framework'] == 'epydoc': 
            if 'needed_conf_file' in kwargs: 
                fdoc.addStep(BuildDocEpy, doc_dir = kwargs['doc_dir'],
                          needed_conf_file = kwargs['needed_conf_file']) 
            elif kwargs['framework'] == 'sphinx': 
                fdoc.addStep(BuildDocSphinx, doc_dir=kwargs['doc_dir'])
    
    return fdoc 
    

def createnamelist(namelist, string):
    """
    createnamelist creates a list of slaves names which name contains string 
    
    :parameter namelist: List of slave names 
    :type namelist: list of strings 
    :parameter string: part of slave name to look for 
    :type string: string
    """ 
    
    temp = []
    for element in namelist:
        if string in element:
            temp.append(element)
    return temp

def createslavelist():
    """
    creates a list of slaves from the slaves.cfg file 
    
     :return: returns list of names of the slave and 
       list of BuildSlave objects
    """ 
    slavelist = []
    namelist = []
    slave_file = open("slaves.cfg", "r")

    temp = slave_file.readlines()

    for line in temp:
        temp2 = line.split(" ", 2)
        temp2[1] = temp2[1].replace("\n", "")
        slavelist.append(BuildSlave(temp2[0], temp2[1]))
        namelist.append(temp2[0])

    return slavelist, namelist