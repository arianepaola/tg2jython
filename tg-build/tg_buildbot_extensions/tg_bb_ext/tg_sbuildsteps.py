""" This module contains the slave-side classes of the
Turbogears-specific buildsteps""" 

__program__   = "tg_sbuildsteps.py"
__author__    = "Steven Mohr"
__version__   = "0.1.0.5"
__revision__  = "$Rev:$"
__date__      = "$Date:$"
__copyright__ = "MIT license"

import os
from tg_bb_ext.winunix import correctseperator, createpath, correctpathdepth
from buildbot.slave.registry import registerSlaveCommand
from buildbot.slave.commands import SlaveShellCommand, \
    command_version, ShellCommand


class SlaveEasyInstall(SlaveShellCommand):
    """slave-side representation of EasyInstall step"""
    def start(self):
        """This function is called when the build step is started"""
        args = self.args
        assert ('package' in args) or ('localinstall' in args)  
        
        env = args['env']
        if 'URL' in args:
            url = "-f "+ args['URL']
        
        env['PATH'] = createpath(args['workdir'])
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])

        newworkdir = correctseperator(args['workdir'])
        workdir = os.path.join(self.builder.basedir, newworkdir)
        
        if 'localinstall' in args and args['localinstall']:
            if os.path.exists(os.path.join(workdir, 'dist')):
                workdir = os.path.join(workdir, 'dist')
            dir_content = os.listdir(workdir)
            for element in dir_content:
                if ".egg" in element\
                and os.path.isfile(os.path.join(workdir,element)):
                    args['package'] = [os.path.join(workdir, element)]

        if 'URL' in args:
            commandline = ["easy_install", url] + args['package']
        else:
            commandline = ["easy_install"] + args['package']

        env['PATH'] = correctpathdepth(workdir) + env['PATH']
        command = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = command
        return self.command.start()

class SlaveRunSetup(SlaveShellCommand):
    """slave-side representation of RunSetup step"""
    def start(self):
        """This function is called when the build step is started"""
        args = self.args

        env = args.get('env')
        env['PATH'] = createpath(args['workdir'])
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])

        if 'devmode' not in args:
            args['devmode'] = 'install'
        else:
            if args['devmode'] == True:
                args['devmode'] = 'develop'

        if 'test' in args:
            args['devmode'] = 'test'
        newworkdir = correctseperator(args['workdir'])
        workdir = os.path.join(self.builder.basedir, newworkdir)

        commandline = ["python", "setup.py", args['devmode']]

        command = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = command
        return self.command.start()


class SlaveBuildEgg(SlaveShellCommand):
    """slave-side representation of BuildEgg step"""
    def start(self): 
        """This function is called when the build step is started"""
        args = self.args
       
        env = args.get('env')
        
        if 'PATH' in env:
            env['PATH'] = correctseperator(env['PATH']) 
        
        env['PATH'] = createpath(args['workdir'])
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = "."+ os.sep + "bin" + ":"+"."+ os.sep + 'lib'
        newworkdir = correctseperator(args['workdir'])
        workdir = os.path.join(self.builder.basedir, newworkdir)

        commandline = ["python", "setup.py", "bdist_egg"]

        command = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = command
        return self.command.start()

class SlaveNose(SlaveShellCommand):
    """slave-side representation of Nose step"""
    def start(self):
        """This function is called when the build step is started"""
        args = self.args
        
        env = args.get('env')

        env['PATH'] = createpath(args['workdir'])
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])

        newworkdir = correctseperator(args['workdir'])

        workdir = os.path.join(self.builder.basedir, newworkdir)

        commandline = ["nosetests"]
        if 'verbose' in args and args['verbose']:
            commandline.append("-v")

        if 'testdir' in args:
            commandline.append(correctseperator(args['testdir']))
        command = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = command
        return self.command.start()

class SlaveBuildEggEE(SlaveShellCommand):
    """slave-side representation of BuildEggEE step"""
    def start(self):
        """This function is called when the build step is started"""
        args = self.args
        assert 'package' in args

        env = args.get('env')
         
        env['PATH'] = createpath(args['workdir'])
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])
        newworkdir = correctseperator(args['workdir'])

        workdir = os.path.join(self.builder.basedir, newworkdir)       

        commandline = ["easy_install", "-zmxd", ".", args['package']]

        part1 = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        part1.start()

        commandline = ["easy_install", "-H", "None", "-f", ".", \
                       args['package']]
        command = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = command
        return self.command.start()


class SlaveInterOSShellCommand(SlaveShellCommand):
    """slave-side representation of InterOSShellCommand step"""
    def start(self):
        """This function is called when the build step is started"""
        args = self.args
        newworkdir = correctseperator(args['workdir'])
        workdir = os.path.join(self.builder.basedir, newworkdir)

        env = args.get('env')
        
        env['PATH'] = createpath(args['workdir'])
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])
        
        commandline = args['command']
        newcommandline = []
        for lines in commandline:
            lines = correctseperator(lines)
            newcommandline.append(lines)

        command = ShellCommand(self.builder, newcommandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = command
        return self.command.start()
  
class SlavePython(SlaveShellCommand):
    """slave-side representation of Python step"""
    def start(self):
        """This function is called when the build step is started"""
        args = self.args
        assert 'script' in args
        env = args['env']
        arguments = []
        if 'script_args' in args:
            arguments = args['script_args']
        
        env['PATH'] = createpath(args['workdir'])
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])

        newworkdir = correctseperator(args['workdir'])
        workdir = os.path.join(self.builder.basedir, newworkdir)
        script = correctseperator(args['script'])

        commandline = ["python"] + [script] + arguments

        command = ShellCommand(self.builder, commandline,
                         workdir, env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = command
        return self.command.start()

    
class SlaveVirtualEnv(SlaveShellCommand):
    """slave-side representation of VirtualEnv step"""
    def start(self):
        """This function is called when the build step is started"""
        args = self.args
        newworkdir = correctseperator(args['workdir'])
        workdir = os.path.join(self.builder.basedir, newworkdir)

        env = args.get('env')
        
        env['PATH'] = createpath(args['workdir'])
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])
        
        commandline = ["../../virtualenv", "--no-site-packages", "./"]
        
        newcommandline = []
        for lines in commandline:
            newcommandline.append(correctseperator(lines))
            
            
        command = ShellCommand(self.builder, newcommandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = command         
        return self.command.start()
    

class SlavePaver(SlaveShellCommand):
    """slave-side representation of Paver step"""
    def start(self):
        """This function is called when the build step is started"""
        args = self.args
        assert args['mode'] is not None
        
        env = args.get('env')
        
        newworkdir = correctseperator(args['workdir'])
        
        env['PATH'] = createpath(args['workdir'])
        
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])



        workdir = os.path.join(self.builder.basedir, newworkdir)
        commandline = ["paver", args['mode']]

        command = ShellCommand(self.builder, commandline,
                         workdir, env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = command
        return self.command.start()


class SlaveDownloadSourceEE(SlaveShellCommand):
    """slave-side representation of DownloadSourceEE step"""
    def start(self):
        """This function is called when the build step is started"""
        args = self.args
        assert 'package' in args
        env = args.get('env')
        
        env['PATH'] = createpath(args['workdir'])
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])
        newworkdir = correctseperator(args['workdir'])

        workdir = os.path.join(self.builder.basedir, newworkdir)

        commandline = ["easy_install", "-eb."] + args['package']

        command = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = command
        return self.command.start()


class SlaveCleanDir(SlaveShellCommand):
    """slave-side representation of CleanDir step"""
    def start(self):
        """This function is called when the build step is started"""
        args = self.args
        env = {}
        newworkdir = correctseperator(args['workdir'])

        workdir = os.path.join(self.builder.basedir, newworkdir)
        
        if os.name == "nt":
            commandline = ["rd", "/q", "/s", self.builder.basedir]
        else:
            commandline = ["rm", "-rf", "*"]

        command = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = command
        return self.command.start()


class SlaveUploadEgg(SlaveShellCommand):
    """slave-side representation of UploadEgg step"""
    def start(self):
        """This function is called when the build step is started"""
        args = self.args
        env = {}
        newworkdir = correctseperator(args['workdir'])
        workdir = os.path.join(self.builder.basedir, newworkdir)
        searchdir = workdir
        if os.path.exists(os.path.join(workdir, 'dist')):
            searchdir = os.path.join(workdir, 'dist')
        dir_content = os.listdir(searchdir)
        for element in dir_content:
            if ".egg" in element\
            and os.path.isfile(os.path.join(searchdir, element)):
                name = os.path.join(searchdir, element)
        
        commandline = ["python", "upload_script.py"] + args['package'] + [name]

        command = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = command
        return self.command.start()


class SlaveBuildDocEpy(SlaveShellCommand):
    """slave-side representation of BuildDocEpy step"""
    def start(self):
        """This function is called when the build step is started"""
        args = self.args
        env = {}
        
        if 'doc_dir' not in args:
            doc_dir = os.path.join(self.builder.basedir, 'build')
        else:
            doc_dir = correctseperator(args['doc_dir'])
            doc_dir = os.path.join(self.builder.basedir, 'build', doc_dir) 
         
        env['PATH'] = createpath('build')
        
        workdir = os.path.join(self.builder.basedir,"build")

        if 'needed_conf_file' in args:
            commandline = ["epydoc", "--config", args['needed_conf_file']]
        else:
            commandline = ["epydoc", "-o", "gen_doc", "--html"] + [doc_dir]
                
        command = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = command
        return self.command.start()


def register_own_steps():
    """registers all custom steps so that it's possible to use them"""
    registerSlaveCommand("EasyInstall", SlaveEasyInstall, command_version)
    registerSlaveCommand("BuildDocEpy", SlaveBuildDocEpy, command_version)
    registerSlaveCommand("UploadEgg", SlaveUploadEgg, command_version)
    registerSlaveCommand("CleanDir", SlaveCleanDir, command_version)
    registerSlaveCommand("DownloadSourceEE", SlaveDownloadSourceEE, \
                         command_version)
    registerSlaveCommand("Paver", SlavePaver, command_version)
    registerSlaveCommand("VirtualEnv", SlaveVirtualEnv, command_version)
    registerSlaveCommand("Python", SlavePython, command_version)
    registerSlaveCommand("BuildEgg", SlaveBuildEgg, command_version)    
    registerSlaveCommand("InterOSShellCommand", SlaveInterOSShellCommand, \
                          command_version)  
    registerSlaveCommand("BuildEggEE", SlaveBuildEggEE, command_version)
    registerSlaveCommand("Nose", SlaveNose, command_version)
    registerSlaveCommand("RunSetup", SlaveRunSetup, command_version)
