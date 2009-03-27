=======================================
Buildmaster documentation
=======================================

:Author: Steven Mohr
:Date: $Date$
:Revision: $Rev$
:Status: Draft

.. contents::

Config files
-------------
slaves.cfg
+++++++++++
This file contains a list of all slaves with their passwords. The structure is very simple. It's just one line per slave which contains the name and the password 
seperated a space. Pay attention that the last line isn't empty.

config options
***************

master.cfg
+++++++++++
This is the config file of the build master. This file is interpreted by the python interpreter so you can use all python commands you want to.
To keep this file short and simple the definition of the build task takes place in tgbuilder.py

Scripts
--------
tgbuilder.py
+++++++++++++
tgbuilder.py contains all builder (TG1, TG1.1, TG2, dependencies via SVN or easy_install) and some functions.

ppath.py
+++++++++
ppath.py contains functions to manipulate the python path.

autobuild_quickstarts.py
+++++++++++++++++++++++++++++++
This scripts creates all possible quickstart projects. It combines Identity (enabled/diabled), Kid/Genshi and SQLObject/Elixir/Alchemy.

Build task functions
---------------------

tg10builder
++++++++++++

New build steps
-------------------
There are a few new build steps to simplify the creation of new builders.

Common parameter
+++++++++++++++++
This parameter is optional. 

workdir
  directory to work in. The base is root directory of the build task.

VirtualEnv
+++++++++++
This buildstep creates a virtual environment.

workdir
  workdir is the only required parameter for this step. You can (or should) use relative paths. 

Python
+++++++
This buildstep runs a python script on the slave side.

script
  the script to execute
script_args
  arguments passed to the script (optional)
  
RunSetup
+++++++++
This step executes a setup.py script with "install" as a argument.

devmode
  If devmode is set RunSetup uses the 'develop' argument instead of 'install'
    
EasyInstall
+++++++++++
This buildstep installs a package via easy_install.
 
package
  name of the package    
workdir
  the workdir is for this step is the build directory. It can't be modified.
localinstall
  installs an egg which is present in workdir or in workdir/dist
  
Nose
+++++
This buildsteps runs nose in the specified directory.

testdir
  this is a directory relative to the workdir where nose starts to search for test cases
workdir
  workdir has to be set for this step.
verbose
  This argument sets the 'verbose' flag for nose.
  
BuildEgg
+++++++++
This buildstep builds an egg.

workdir
  workdir has to be set for this step
  
BuildEggEE
+++++++++++
This step downloads the source via EasyInstall and  builds an egg.

package
  name of the package which egg should be created

InterOSShell
++++++++++++
This step is equal to ShellCommand but it corrects OS-specific path seperators.

command
  the command which should be executed on the slave side
  
Paver
++++++
This step runs paver with the specified options

mode
  specifies the mode to start paver

CleanDir
+++++++++
This steps deletes all files in workdir.
 
UploadEgg
++++++++++
Uploads an egg to Turbogears PackageIndex. It uses the .pypirc in the home directory of the user to
authorize the upload.
 
package
  name of the package name which should be uploaded

BuildDoc
+++++++++
Builds documentition via epydoc or sphinx.

doc_dir
  directory with source which documentation should be built
framework
  selects if "epydoc" or "sphinx" should be used. default is epydoc