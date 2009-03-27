from buildbot.process import factory
from buildbot.steps.shell import ShellCommand
from buildbot.steps.transfer import FileDownload
from buildbot.steps import source
import os
from ppath import *
from buildbot.buildslave import BuildSlave
from tg_mbuildsteps import * 

""" This module contains functions to automate creation of BuildFactories and other helpful functions to use in master.cfg"""

#################### TG 1.0 builder ###################################
def tg10builder(pythonpath,quick=False):
    """tg10builder returns a BuildFactory which downloads TG1.0 from SVN,installs all dependencies, runs the core tests, creates all posible quickstart projects,
    runs the tests for all of this projects and builds the egg. pythonpath is the path, which is used for all python scripts. pythonpath must fit the pattern: "binDir:libDir". """

    ftg1 = factory.BuildFactory()
    if quick:
        ftg1.addStep(source.SVN(mode='update',svnurl='http://svn.turbogears.org/branches/1.0'))
    else:
        ftg1.addStep(source.SVN(mode='clobber',svnurl='http://svn.turbogears.org/branches/1.0'))
        ftg1.addStep(FileDownload,mastersrc="autobuild_quickstarts.py",slavedest="autobuild_quickstarts.py")
        ftg1.addStep(FileDownload,mastersrc="upload_script.py",slavedest="upload_script.py")
    
    ftg1.addStep(VirtualEnv, env={'PYTHONPATH':pythonpath},haltOnFailure=True)
    ftg1.addStep(InterOSShellCommand,command=["cp","python2.3","python"],description="Rename python23",
                 workdir="build/bin",flunkOnFailure=False)

    if quick:
        ftg1.addStep(EasyInstall,package=["cherrypy"],env={'PYTHONPATH':pythonpath},haltOnFailure=True)    
    else:
        ftg1.addStep(Python,script="externals.py",workdir="build/thirdparty",
                 env={'PYTHONPATH':pythonpath},haltOnFailure=True)
        ftg1.addStep(RunSetup,description="Installing TG1",env={'PYTHONPATH':pythonpath},haltOnFailure=True)
        ftg1.addStep(EasyInstall,package=["SQLAlchemy","SQLObject","Genshi", "gsquickstart", "docutils"],
                 env={'PYTHONPATH':pythonpath},haltOnFailure=True)
        
    ftg1.addStep(EasyInstall,package=["nose"],env={'PYTHONPATH':pythonpath},haltOnFailure=True)

    ftg1.addStep(Nose,verbose=True,testdir="turbogears/tests",description="Running nosetest TG",
                 env={'PYTHONPATH':pythonpath},haltOnFailure=True,haltOnFailure=True)
    if quick == False:
        ftg1.addStep(Python,script="autobuild_quickstarts.py",description="Creating quickstart projects",
                 env={'PYTHONPATH':pythonpath})
        ftg1.addStep(Nose,description="Running nosetest Quickstart",
                 env={'PYTHONPATH':pythonpath},testdir="build")
    ftg1.addStep(BuildEgg,description="Building TG1 egg",env={'PYTHONPATH':pythonpath},haltOnFailure=True)
    ftg1.addStep(EasyInstall,env={'PYTHONPATH':pythonpath}, localinstall = True, haltOnFailure = True)
    if quick == False:
        ftg1.addStep(UploadEgg,env={'PYTHONPATH':pythonpath},package=["TurboGears 1"])
    return ftg1


##################### TG 1.1 -Builder ######################

def tg11builder(pythonpath,quick=False):
    """tg11builder returns a BuildFactory which downloads TG1.1 from SVN,installs all dependencies, runs the core tests, creates all posible quickstart projects,
    runs the tests for all of this projects and builds the egg. pythonpath is the path, which is used for all python scripts. pythonpath must fit the pattern: "binDir:libDir". """
    ftg11 = factory.BuildFactory()

    if quick:
        ftg11.addStep(source.SVN(mode='update',svnurl='http://svn.turbogears.org/branches/1.1'))
    else:
        ftg11.addStep(source.SVN(mode='clobber',svnurl='http://svn.turbogears.org/branches/1.1'))
        ftg11.addStep(FileDownload,mastersrc="autobuild_quickstarts.py",slavedest="autobuild_quickstarts.py")
        ftg11.addStep(FileDownload,mastersrc="upload_script.py",slavedest="upload_script.py")
        
    ftg11.addStep(VirtualEnv,env={'PYTHONPATH':pythonpath},haltOnFailure=True)
    
    ftg11.addStep(InterOSShellCommand,command=["cp","python2.3","python"],description="Rename python23",
                 workdir="build/bin",flunkOnFailure=False)
    if quick:
        ftg1.addStep(EasyInstall,package=["cherrypy"],env={'PYTHONPATH':pythonpath},haltOnFailure=True)
    else:
        ftg11.addStep(Python,script="externals.py",description="Running externals.py",
                  workdir="build/thirdparty",env={'PYTHONPATH':pythonpath},haltOnFailure=True)
        ftg11.addStep(RunSetup,description="Installing TG11",env={'PYTHONPATH':pythonpath},haltOnFailure=True)

        ftg11.addStep(EasyInstall,package=["SQLAlchemy","SQLObject","Genshi","gsquickstart","docutils"],
                      description="Installing Dependencies",env={"PYTHONPATH":pythonpath},haltOnFailure=True)

    ftg11.addStep(EasyInstall,package=["nose"],description="installing nose",env={'PYTHONPATH':pythonpath},haltOnFailure=True)
    ftg11.addStep(Nose,testdir="turbogears/tests",verbose=True,description="Running nosetest TG",
                  env={'PYTHONPATH':pythonpath},haltOnFailure=True)
    
    if quick == False:
        ftg11.addStep(Python,script="autobuild_quickstarts.py",description="Creating quickstart projects",
                  env={'PYTHONPATH':pythonpath},haltOnFailure=True)
        ftg11.addStep(Nose,description="Running nosetest Quickstart",env={'PYTHONPATH':pythonpath})

    ftg11.addStep(BuildEgg,description="Building TG11 egg",env={'PYTHONPATH':pythonpath},haltOnFailure=True)
    ftg11.addStep(EasyInstall,env={'PYTHONPATH':pythonpath}, localinstall = True, haltOnFailure = True)
    if quick==False:
        ftg11.addStep(UploadEgg,env={'PYTHONPATH':pythonpath},package=["TurboGears 1.1"])
    return ftg11

######################### TG 2 -Builder ########################
def tg2builder(pythonpath,quick=False):
    """tg2builder returns a BuildFactory which downloads TG2 from SVN, downloads pylons from mercurial, installs all dependencies, runs the core tests, creates all posible quickstart projects,
    runs the tests for all of this projects and builds the egg. pythonpath is the path, which is used for all python scripts. pythonpath must fit the pattern: "binDir:libDir"."""
    partsofppath = splitppath(pythonpath)
    ftg2 = factory.BuildFactory()
    if quick:
        ftg2.addStep(source.Mercurial(repourl="http://pylonshq.com/hg/pylons-dev",mode='update',workdir="build/pylons"),haltOnFailure=True)
        ftg2.addStep(source.SVN(mode='update',svnurl='http://svn.turbogears.org/projects/tg.devtools/trunk',workdir='build/tgdev'),haltOnFailure=True)
        ftg2.addStep(source.SVN(mode='update',svnurl='http://svn.turbogears.org/trunk',workdir='build/tg2',haltOnFailure = False))
        ftg2.addStep(source.SVN(mode='update',svnurl='http://svn.turbogears.org/projects/tgrepozewho/trunk',workdir='build/tgreoz'),haltOnFailure=True)
    else:
        ftg2.addStep(source.Mercurial(repourl="http://pylonshq.com/hg/pylons-dev",mode='clobber',workdir="build/pylons"),haltOnFailure=True)
        ftg2.addStep(source.SVN(mode='clobber',svnurl='http://svn.turbogears.org/projects/tg.devtools/trunk',workdir='build/tgdev'),haltOnFailure=True)
        ftg2.addStep(source.SVN(mode='clobber',svnurl='http://svn.turbogears.org/trunk',workdir='build/tg2',haltOnFailure = True))
        ftg2.addStep(source.SVN(mode='clobber',svnurl='http://svn.turbogears.org/projects/tgrepozewho/trunk',workdir='build/tgreoz'),haltOnFailure=True)
        ftg2.addStep(source.Mercurial(repourl="https://www.knowledgetap.com/hg/webhelpers",mode='clobber',workdir="build/webhelpers"),haltOnFailure=True)
        ftg2.addStep(FileDownload,mastersrc="upload_script.py",slavedest="upload_script.py")
        ftg2.addStep(FileDownload,mastersrc="autobuild_quickstarts.py",slavedest="autobuild_quickstarts.py")
    
    ftg2.addStep(VirtualEnv,env={'PYTHONPATH':pythonpath},haltOnFailure=True)

    ftg2.addStep(EasyInstall,package=["nose"],description="installing nose",env={'PYTHONPATH':pythonpath},haltOnFailure=True)

    ftg2.addStep(EasyInstall,package=["paver"],description="Installing paver",env={'PYTHONPATH':pythonpath})
    if quick == False:
        ftg2.addStep(EasyInstall,URL="http://turbogears.org/download/",package=["RuleDispatch","PyProtocols"],description="Installing RuleDispatch + Pyprotocols",env={'PYTHONPATH':pythonpath})

        newppath = modifyppath(pythonpath,"..")

        ftg2.addStep(RunSetup,devmode=True,description="Installing webhelpers",env={'PYTHONPATH':newppath},
                 workdir="build/webhelpers")
        ftg2.addStep(RunSetup,devmode=True,description="Installing pylons",env={'PYTHONPATH':newppath},
                 workdir="build/pylons",haltOnFailure=True)
        ftg2.addStep(RunSetup,devmode=True,description="Installing tgreozewho",env={'PYTHONPATH':newppath},
                 workdir="build/tgreoz")
        ftg2.addStep(Paver,description="Installing tg2",mode='develop',env={'PYTHONPATH':newppath},
                 workdir="build/tg2",haltOnFailure=True)
        ftg2.addStep(RunSetup,devmode=True,description="Installing tgdev",
                 env={'PYTHONPATH':newppath},workdir="build/tgdev")
    
    ftg2.addStep(Nose,testdir="tg2/tg",verbose=True,haltOnFailure=True)
    ftg2.addStep(Nose,testdir="tgdev/devtools",verbose=True)
    ftg2.addStep(Nose,testdir="tgreoz/tgrepozewho",verbose=True)
    
    if quick == False:
        ftg2.addStep(Python,script="autobuild_quickstarts.py",script_args=["TG2"],env={'PYTHONPATH':pythonpath},
                 description="Creating quickstart projects",workdir="build")
        ftg2.addStep(Nose,description="Running nosetest Quickstart",env={'PYTHONPATH':pythonpath})
        
    ftg2.addStep(Paver,mode="bdist_egg",description="Building TG2 egg",
                 env={'PYTHONPATH':pythonpath},haltOnFailure=True)
    ftg2.addStep(EasyInstall,env={'PYTHONPATH':pythonpath}, localinstall = True, haltOnFailure = True)
    if quick == False:
        ftg2.addStep(UploadEgg,env={'PYTHONPATH':pythonpath},package=["TurboGears 2"])
    return ftg2

def dependencybuildersvn(svn_url,pythonpath,name,dependencyfromtg=None):
    """ dependencybuildersvn creates a build factory which does a checkout from svnURL, downloads the dependencies specified in DependencyFromTG from the TurboGears server,
    runs setup.py and builds the egg."""
    
    f = factory.BuildFactory()
    f.addStep(source.SVN(svnurl=svn_url,mode='clobber'))
    f.addStep(FileDownload,mastersrc="upload_script.py",slavedest="upload_script.py")
    f.addStep(VirtualEnv,env={'PYTHONPATH':pythonpath},haltOnFailure=True)
    f.addStep(EasyInstall,package=["nose"],env={'PYTHONPATH':pythonpath},haltOnFailure=True)
    
    if dependencyfromtg is not None  :
        f.addStep(EasyInstall,URL="http://turbogears.org/download/",
                  description="Installing Dependencies",package=dependencyfromtg,env={'PYTHONPATH':pythonpath})
    f.addStep(RunSetup,description="Installing "+name,env={'PYTHONPATH':pythonpath})
    f.addStep(Python,script="setup.py",script_args=["test"],description="Testing "+name, env={'PYTHONPATH':pythonpath},workdir="build",haltOnFailure=True)
    f.addStep(BuildEgg,env={'PYTHONPATH':pythonpath},haltOnFailure=True)
    f.addStep(EasyInstall,env={'PYTHONPATH':pythonpath}, localinstall = True, haltOnFailure = True)
    f.addStep(UploadEgg,env={'PYTHONPATH':pythonpath},package=[name])
    return f

def dependencybuilderee(name,pythonpath):
    """dependencybuilderee creates a build factory which downloads the source of the dependency via easy_install and builds the egg."""
    f = factory.BuildFactory()
    f.addStep(CleanDir)
    f.addStep(FileDownload,mastersrc="upload_script.py",slavedest="upload_script.py")
    f.addStep(VirtualEnv,env={'PYTHONPATH':pythonpath},haltOnFailure=True)
    f.addStep(EasyInstall,package=["Nose"])
    f.addStep(BuildEggEE,package=name[0], env={'PYTHONPATH':pythonpath})
    f.addStep(EasyInstall,env={'PYTHONPATH':pythonpath}, localinstall = True, haltOnFailure = True)
    f.addStep(UploadEgg,env={'PYTHONPATH':pythonpath},package=name)
    return f

def tg_ng_setupbuilder(pythonpath):
    f = factory.BuildFactory()
    f.addStep(CleanDir)
    f.addStep(FileDownload,mastersrc="create-tgsetupng.py",slavedest="create-tgsetupng.py")
    f.addStep(Python,script="create-tgsetupng.py",haltOnFailure=True)
    f.addStep(Python,script="tgsetupng.py",script_args=["tg"],haltOnFailure=True)
    return f

def doc_builder(pythonpath,**kwargs):
    f = factory.BuildFactory()
    if 'framework' not in kwargs:
        kwargs['framework'] = 'epydoc'
        
    if 'doc_dir' not in kwargs:
        kwargs['doc_dir'] = ''
        
    if 'package' in kwargs:
        f.addStep(CleanDir)
        f.addStep(DownloadSourceEE,package=kwargs['package'])
    else:
        f.addStep(source.SVN,svnurl=kwargs['svnurl'], mode='clobber')
    f.addStep(BuildDoc, framework=kwargs['framework'],doc_dir=kwargs['doc_dir'])
    return f
    

def createnamelist(namelist,string):
    """createnamelist creates a list of slaves names which name contains string"""
    temp = []
    for element in namelist:
        if string in element:
            temp.append(element)
    return temp

def createslavelist():
    """creates a list of slaves from the slaves.cfg file"""
    slavelist = []
    namelist = []
    file = open("slaves.cfg","r")

    temp =file.readlines()

    for line in temp:
        temp2 = line.split(" ",2)
        temp2[1] = temp2[1].replace("\n","")
        slavelist.append(BuildSlave(temp2[0],temp2[1]))
        namelist.append(temp2[0])

    return slavelist,namelist
    


