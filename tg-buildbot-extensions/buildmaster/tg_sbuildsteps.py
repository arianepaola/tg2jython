""" This module contains the slave-side classes of the Turbogears-specific buildsteps""" 


__program__   = "tg_sbuildsteps.py"
__author__    = "Steven Mohr"
__version__   = "0.1"
__revision__  = "$Rev:$"
__date__      = "$Date:$"
__copyright__ = "MIT license"

from winunix import correctseperator, correctpathdepth


class SlaveEasyInstall(SlaveShellCommand):
    def start(self):
        args = self.args
        assert ('package' in args) or ('localinstall' in args)  
        
        env = args['env']
        if 'URL' in args:
            url = "-f "+ args['URL']
        
        if 'PATH' in env:
            env['PATH'] = correctseperator(env['PATH']) 
        if os.sep == '\\':
            env['PATH'] = 'scripts' + os.path.pathsep + os.getenv("PATH")
        else:
            env['PATH'] = 'bin' + os.path.pathsep + os.getenv("PATH")
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])

        newworkdir = correctseperator(args['workdir'])
        workdir = os.path.join(self.builder.basedir,newworkdir)
        
        if 'localinstall' in args and args['localinstall']:
            if os.path.exists(os.path.join(workdir,'dist')):
                workdir = os.path.join(workdir,'dist')
            dir_content = os.listdir(workdir)
            for element in dir_content:
                if ".egg" in element and os.path.isfile(os.path.join(workdir,element)):
                        args['package'] = [os.path.join(workdir,element)]
                

        if 'URL' in args:
            commandline = ["easy_install",url] + args['package']
        else:
            commandline = ["easy_install"]+ args['package']
        

        c = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()
        return d
    
registerSlaveCommand("EasyInstall", SlaveEasyInstall, command_version)

class SlaveRunSetup(SlaveShellCommand):
    def start(self):
        args = self.args

        env = args.get('env')
        if 'PATH' in env:
            env['PATH'] = correctseperator(env['PATH']) 
        
        if os.sep == '\\':
            env['PATH'] = correctpathdepth(args['workdir']) + 'scripts' + os.path.pathsep + os.getenv("PATH")
        else:
            env['PATH'] = correctpathdepth(args['workdir']) + 'bin' + os.path.pathsep + os.getenv("PATH")
        
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

        if os.name =='nt':
            commandline = ["python","setup.py",args['devmode']]
        else:
            commandline = ["python","setup.py",args['devmode']]
            
        if os.name =='nt':
            commandline.insert(2,"build")
            commandline.insert(3,"--compiler=mingw32")

        c = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()
        return d

registerSlaveCommand("RunSetup", SlaveRunSetup, command_version)
class SlaveBuildEgg(SlaveShellCommand):
    def start(self): 
        args = self.args
       
        env = args.get('env')
        
        if 'PATH' in env:
            env['PATH'] = correctseperator(env['PATH']) 
        
        if os.sep == '\\':
            env['PATH'] = correctpathdepth(args['workdir']) + 'scripts' + os.path.pathsep + os.getenv("PATH")
        else:
            env['PATH'] = correctpathdepth(args['workdir']) + 'bin' + os.path.pathsep + os.getenv("PATH")
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = "."+ os.sep + "bin" + ":"+"."+ os.sep + 'lib'
        newworkdir = correctseperator(args['workdir'])
        workdir = os.path.join(self.builder.basedir, newworkdir)


        commandline = ["python","setup.py","bdist_egg"]
            
        if os.name =='nt':
            commandline.insert(2,"build")
            commandline.insert(3,"--compiler=mingw32")

        c = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()
        return d
    
registerSlaveCommand("BuildEgg", SlaveBuildEgg, command_version)

class SlaveNose(SlaveShellCommand):
    def start(self):
        args = self.args
        
        env = args.get('env')
        if 'PATH' in env:
            env['PATH'] = correctseperator(env['PATH']) 
        if os.sep == '\\':
            env['PATH'] = correctpathdepth(args['workdir']) + 'scripts' + os.path.pathsep + os.getenv("PATH")
        else:
            env['PATH'] = correctpathdepth(args['workdir']) + 'bin' + os.path.pathsep + os.getenv("PATH")
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])

        newworkdir = correctseperator(args['workdir'])

        workdir = os.path.join(self.builder.basedir, newworkdir)

        commandline = ["nosetests"]
        if 'verbose' in args and args['verbose']:
            commandline.append("-v")

        if args.has_key('testdir'):
            commandline.append(correctseperator(args['testdir']))
        c = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()
        return d
registerSlaveCommand("Nose", SlaveNose, command_version)
class SlaveBuildEggEE(SlaveShellCommand):
    def start(self):
        args = self.args
        assert 'package' in args

        env = args.get('env')
        
        
        if 'PATH' in env:
            env['PATH'] = correctseperator(env['PATH']) 
        if os.sep == '\\':
            env['PATH'] = 'scripts' + os.path.pathsep + os.getenv("PATH")
        else:
            env['PATH'] = 'bin' + os.path.pathsep + os.getenv("PATH")
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])
        newworkdir = correctseperator(args['workdir'])

        workdir = os.path.join(self.builder.basedir, newworkdir)
        

        commandline = ["easy_install","-zmxd",".",args['package']]

        c = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()

        commandline = ["easy_install","-H","None","-f",".",args['package']]
        c = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()
        return d
registerSlaveCommand("BuildEggEE", SlaveBuildEggEE, command_version)

class SlaveInterOSShellCommand(SlaveShellCommand):
    def start(self):
        args = self.args
        newworkdir = correctseperator(args['workdir'])
        workdir = os.path.join(self.builder.basedir, newworkdir)

        env = args.get('env')
        
        if 'PATH' in env:
            env['PATH'] = correctseperator(env['PATH']) 
        if os.sep == '\\':
            env['PATH'] = correctpathdepth(args['workdir']) + 'scripts' + os.path.pathsep + os.getenv("PATH")
        else:
            env['PATH'] = correctpathdepth(args['workdir']) + 'bin' + os.path.pathsep + os.getenv("PATH")
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])
        
        commandline = args['command']
        newcommandline = []
        for lines in commandline:
            lines = correctseperator(lines)
            newcommandline.append(lines)

        c = ShellCommand(self.builder, newcommandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()
        return d
registerSlaveCommand("InterOSShellCommand", SlaveInterOSShellCommand, command_version)    
class SlavePython(SlaveShellCommand):
    def start(self):
        args = self.args
        assert 'script' in args
        
        env = args['env']
        
        arguments = []
        if 'script_args' in args:
            arguments = args['script_args']
        
        if 'PATH' in env:
            env['PATH'] = correctseperator(env['PATH'])
        
        if os.path.sep == '\\':
            env['PATH'] = correctpathdepth(args['workdir']) + 'scripts' + os.path.pathsep + os.getenv("PATH")
        else:
            env['PATH'] = correctpathdepth(args['workdir']) + 'bin' + os.path.pathsep + os.getenv("PATH")
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])

        newworkdir = correctseperator(args['workdir'])
        workdir = os.path.join(self.builder.basedir, newworkdir)
        script = correctseperator(args['script'])

        commandline = ["python"]+[script] + arguments

        c = ShellCommand(self.builder, commandline,
                         workdir, env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()
        return d
registerSlaveCommand("Python", SlavePython, command_version)
    
class SlaveVirtualEnv(SlaveShellCommand):
    def start(self):
        args = self.args
        newworkdir = correctseperator(args['workdir'])
        workdir = os.path.join(self.builder.basedir, newworkdir)

        env = args.get('env')
        
        if 'PATH' in env:
            env['PATH'] = correctseperator(env['PATH']) 
        if os.sep == '\\':
            env['PATH'] = correctpathdepth(args['workdir']) + 'scripts' + os.path.pathsep + os.getenv("PATH")
        else:
            env['PATH'] = correctpathdepth(args['workdir']) + 'bin' + os.path.pathsep + os.getenv("PATH")
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])
        
        commandline = ["../../virtualenv","--no-site-packages","./"]
        
        newcommandline = []
        for lines in commandline:
            newcommandline.append(correctseperator(lines))
            
            
        c = ShellCommand(self.builder, newcommandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()
            
        return d
registerSlaveCommand("VirtualEnv", SlaveVirtualEnv, command_version)      

class SlavePaver(SlaveShellCommand):
    def start(self):
        args = self.args
        assert args['mode'] is not None
        
        env = args.get('env')
        
        newworkdir = correctseperator(args['workdir'])
        
        
       
        
        if os.path.sep == '\\':
            env['PATH'] = correctpathdepth(newworkdir) + 'scripts' + os.path.pathsep + os.getenv("PATH")
        else:
            env['PATH'] = correctpathdepth(newworkdir) + 'bin' + os.path.pathsep + os.getenv("PATH")
        
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])



        workdir = os.path.join(self.builder.basedir, newworkdir)
        commandline = ["paver",args['mode']]

        c = ShellCommand(self.builder, commandline,
                         workdir, env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()
        return d
registerSlaveCommand("Paver", SlavePaver, command_version)

class SlaveDownloadSourceEE(SlaveShellCommand):
    def start(self):
        args = self.args
        assert 'package' in args

        env = args.get('env')
        
        
        if 'PATH' in env:
            env['PATH'] = correctseperator(env['PATH']) 
        if os.sep == '\\':
            env['PATH'] = 'scripts' + os.path.pathsep + os.getenv("PATH")
        else:
            env['PATH'] = 'bin' + os.path.pathsep + os.getenv("PATH")
        
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = correctseperator(env['PYTHONPATH'])
        newworkdir = correctseperator(args['workdir'])

        workdir = os.path.join(self.builder.basedir, newworkdir)
        

        commandline = ["easy_install","-eb."] + args['package']

        c = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()

        return d
registerSlaveCommand("DownloadSourceEE", SlaveDownloadSourceEE, command_version)

class SlaveCleanDir(SlaveShellCommand):
    def start(self):
        args = self.args


        env = {}
        newworkdir = correctseperator(args['workdir'])

        workdir = os.path.join(self.builder.basedir, newworkdir)
        if os.name =="nt":
            commandline = ["rd","/q","/s",self.builder.basedir]
        else:
            commandline = ["rm","-rf","*"]

        c = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()
        return d
registerSlaveCommand("CleanDir", SlaveCleanDir, command_version)

class SlaveUploadEgg(SlaveShellCommand):
    def start(self):
        args = self.args
        env = {}
        newworkdir = correctseperator(args['workdir'])
        workdir = os.path.join(self.builder.basedir, newworkdir)
        searchdir = workdir
        if os.path.exists(os.path.join(workdir,'dist')):
                searchdir = os.path.join(workdir,'dist')
        dir_content = os.listdir(searchdir)
        for element in dir_content:
            if ".egg" in element and os.path.isfile(os.path.join(searchdir,element)):
                name = os.path.join(searchdir,element)
        
        commandline = ["python","upload_script.py"] + args['package'] + [name] 

        c = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()
        return d
registerSlaveCommand("UploadEgg", SlaveUploadEgg, command_version)

class SlaveBuildDoc(SlaveShellCommand):
    def start(self):
        args = self.args
        env = {}
        
        if 'doc_dir' not in args:
            doc_dir = os.path.join(self.builder.basedir,'build')
        else:
            doc_dir = correctseperator(args['doc_dir'])
            doc_dir = os.path.join(self.builder.basedir,'build',doc_dir) 
         
        if os.sep == '\\':
            env['PATH'] = 'scripts' + os.path.pathsep + os.getenv("PATH")
        else:
            env['PATH'] = 'bin' + os.path.pathsep + os.getenv("PATH")
        
        workdir = self.builder.basedir
        if 'framework' in args and args['framework'] == 'sphinx':
            commandline = ["sphinx-build","-b","html",doc_dir,"gen_doc"]
        else:
            if args['framework'] == 'script':
                if 'doc_dir' not in args:
                    args['doc_dir'] = "."
                
                commandline = [args["doc_dir"]+os.sep+"build_api_docs.sh"]
                if 'workdir' in args:
                    workdir = os.path.join(self.builder.basedir,args['workdir'])
                else:
                    workdir = os.path.join(self.builder.basedir,'build')
            else:
                commandline = ["epydoc","-o","gen_doc","--html"] + [doc_dir]
                
        c = ShellCommand(self.builder, commandline,
                         workdir, environ=env,
                         timeout=args.get('timeout', None),
                         sendStdout=args.get('want_stdout', True),
                         sendStderr=args.get('want_stderr', True),
                         sendRC=True,
                         initialStdin=args.get('initial_stdin'),
                         keepStdinOpen=args.get('keep_stdin_open'),
                         logfiles=args.get('logfiles', {}),
                         )
        self.command = c
        d = self.command.start()

        return d
registerSlaveCommand("BuildDoc", SlaveBuildDoc, command_version)