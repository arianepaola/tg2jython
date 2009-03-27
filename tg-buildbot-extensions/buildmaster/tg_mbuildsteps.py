__program__   = "tg_buildsteps.py"
__author__    = "Steven Mohr"
__version__   = "0.1"
__revision__  = "$Rev:$"
__date__      = "$Date:$"
__copyright__ = "MIT license"

"""This module contains all TG-specific master-side part of the new build steps"""


from buildbot.process.buildstep import LoggedRemoteCommand, LoggingBuildStep, BuildStep, OutputProgressObserver


class BaseStep(LoggingBuildStep):
    """Base class for all new build steps
    @keyword description: description of build step while working
    @type description: string
    @keyword descriptionDone: description of build step when finished
    @type descriptionDone: string
    @keyword env: enviroment variables
    @type env: dict of string:string
    @keyword workdir: workdir to work in
    @type workdir: string """
    parms = BuildStep.parms + ['description','descriptionDone','env','workdir']
    def __init__(self, slave_name, *args, **kwargs):
        kwargs['haltOnFailure']=False
        if 'workdir' not in kwargs:
            kwargs['workdir'] = 'build'
        
        if 'env' not in kwargs:
            kwargs['env'] = {}    
        
        if 'description' in kwargs and 'descriptionDone' not in kwargs:
            kwargs['descriptionDone'] = kwargs['description']
        
        self.slave_name = slave_name
        self.arguments = kwargs.copy()
        LoggingBuildStep.__init__(self, *args, **kwargs)
        
    def describe(self, done=False):
        if 'description' in self.arguments:
            if done:
                return [self.arguments['description']]
            else:
                return [self.arguments['descriptionDone']]
        
        else:            
            if done:
                return ["Created ", self.slave_name]
            else:
                return ["Creating ", self.slave_name]   
         
    def start(self):
        cmd = LoggedRemoteCommand(self.slave_name, self.arguments)
        self.startCommand(cmd)      
          
class VirtualEnv(BaseStep):
    """Creates a virtual environment in workdir. This VirtualEnv has no global site packages"""
    parms = BaseStep.parms 
    def __init__(self, *args, **kwargs):
        BaseStep.__init__(self, slave_name="VirtualEnv", *args, **kwargs)
        self.description = "Creating virtual environment"
        self.descriptionDone = "virtual environment created"
                 
class EasyInstall(BaseStep):
    """Runs easy_install script
    @keyword package: package to install
    @type package: list of string
    @keyword URL: location to download egg from
    @type URL: string
    @keyword localinstall: search in workdir and workdir/dist for an egg
    @type localinstall: boolean"""
    parms = BaseStep.parms + ['package','URL','localinstall']    
    def __init__(self, *args, **kwargs):
        if 'package' not in kwargs:
            kwargs['package'] = 'egg'
        BaseStep.__init__(self,  slave_name="EasyInstall", *args, **kwargs) 
        self.description = "Installing " + str(kwargs['package'])
        self.descriptionDone = str(kwargs['package']) + " installed"  
    
class RunSetup(BaseStep):
    """Runs setup.py in workdir
    @keyword devmode: runs setup.py in develop mode
    @type devmode: boolean
    @keyword test: runs setup.py in test mode
    @type test: boolean"""
    parms = BaseStep.parms + ['devmode','test'] 
    def __init__(self, *args, **kwargs):
        BaseStep.__init__(self, slave_name="RunSetup", *args, **kwargs)
        self.description = "Executing setup.py"
        self.descriptionDone = "setup.py executed"

class BuildEgg(BaseStep):
    """Builds an egg. It uses setup.py in workdir with bdist_egg parameter"""
    parms = BaseStep.parms
    def __init__(self, *args, **kwargs):
        BaseStep.__init__(self,  slave_name="BuildEgg", *args, **kwargs)
        self.description = "Building egg"
        self.descriptionDone = "Egg built"
        
class Nose(BaseStep):
    """Nose runs nosetests in testdir
    @keyword verbose: sets verbose flag
    @type verbose: boolean
    @keyword testdir: directory relative to workdir where nosetests searchs for tests
    @type testdir: string"""
    parms = BaseStep.parms + ['verbose','testdir'] 
    def __init__(self, *args, **kwargs):
        BaseStep.__init__(self, slave_name="Nose", *args, **kwargs)
        self.description = "Running nose"
        self.descriptionDone = "nose finished"
        
class BuildEggEE(BaseStep):
    """BuildEggEE builds an egg. It downloads the source from PyPi and builds an egg.
    @keyword package: name of the package
    @type package: string"""
    parms = BaseStep.parms + ['package'] 
    def __init__(self, *args, **kwargs):
        BaseStep.__init__(self, slave_name="BuildEggEE", *args, **kwargs)
        self.description = "Building egg"
        self.descriptionDone = "Egg built"
       
class InterOSShellCommand(BaseStep):
    """InterOSShellCommand does the same as ShellCommand. The only difference is
    that InterOSShellCommand corrects separators.
    @keyword command: command to execute
    @type command: list of strings"""
    parms = BaseStep.parms + ['command'] 
    def __init__(self, *args, **kwargs):
        BaseStep.__init__(self,  slave_name="InterOSShellCommand", *args, **kwargs)
        self.description = "Started shell command"
        self.descriptionDone = "ShellCommand finished"
class Python(BaseStep):
    """Runs a python script
    @keyword script: path to python script
    @type script: string
    @keyword script_args: arguments passed to script
    @type script_args: string"""
    parms = BaseStep.parms + ['script','script_args'] 
    def __init__(self, *args, **kwargs):
        BaseStep.__init__(self,  slave_name="Python", *args, **kwargs) 
        self.description = "Running script"
        self.descriptionDone = "script executed"

class Paver(BaseStep):
    """Runs the paver script
    @keyword mode: paver mode
    @type mode: string"""
    parms = BaseStep.parms + ['mode'] 
    def __init__(self, *args, **kwargs):
        self.description = "Running paver"
        self.descriptionDone = "paver finished"
        BaseStep.__init__(self,  slave_name="Paver", *args, **kwargs)
        
class DownloadSourceEE(BaseStep):
    parms = BaseStep.parms + ['package'] 
    def __init__(self, *args, **kwargs):
        BaseStep.__init__(self, slave_name="DownloadSourceEE", *args, **kwargs)
        
class CleanDir(BaseStep):
    """Deletes all files and directories in workdir"""
    parms = BaseStep.parms 
    def __init__(self, *args, **kwargs):
        BaseStep.__init__(self, slave_name="CleanDir", *args, **kwargs)
        self.description = "Cleaning directory"
        self.descriptionDone = "Directory cleaned"
        
class UploadEgg(BaseStep):
    """Uploads an egg to the PackageIndex instance specified in $HOME/.pypirc.
    @keyword package: name of package which should be uploaded
    @type package: string"""
    parms = BaseStep.parms +['package']
    def __init__(self, *args, **kwargs):
        BaseStep.__init__(self, slave_name="UploadEgg", *args, **kwargs)
        self.description = "Upload started"
        self.descriptionDone = "Upload finished"
        
class BuildDoc(BaseStep):
    """Builds documentation from files contained in doc_dir.
    @keyword doc_dir: directory which contains documentation files
    @type doc_dir: string
    @keyword framework: framework to use: possible values: 'epydoc', 'sphinx', 'script'
    @type framework: string"""
    parms = BaseStep.parms +['doc_dir','framework']
    def __init__(self, *args, **kwargs):
        BaseStep.__init__(self, slave_name="BuildDoc", *args, **kwargs)
        self.description = "Starting documentation"
        self.descriptionDone = "Documentation finished"
        