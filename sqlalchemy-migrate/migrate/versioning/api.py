"""An external API to the versioning system
Used by the shell utility; could also be used by other scripts
"""
import sys
import inspect
from sqlalchemy import create_engine
from migrate.versioning import exceptions,repository,schema,version
import script as script_ #command name conflict

__all__=[
'help',
'create',
'script',
'script_sql',
'make_update_script_for_model',
'version',
'source',
'version_control',
'db_version',
'upgrade',
'downgrade',
'drop_version_control',
'manage',
'test',
'compare_model_to_db',
'create_model',
'update_db_from_model',
]

cls_repository = repository.Repository
cls_schema = schema.ControlledSchema
cls_vernum = version.VerNum
cls_script_python = script_.PythonScript

def help(cmd=None,**opts):
    """%prog help COMMAND

    Displays help on a given command.
    """
    if cmd is None:
        raise exceptions.UsageError(None)
    try:
        func = globals()[cmd]
    except:
        raise exceptions.UsageError("'%s' isn't a valid command. Try 'help COMMAND'"%cmd)
    ret = func.__doc__
    if sys.argv[0]:
        ret = ret.replace('%prog',sys.argv[0]) 
    return ret

def create(repository,name,**opts):
    """%prog create REPOSITORY_PATH NAME [--table=TABLE]

    Create an empty repository at the specified path.

    You can specify the version_table to be used; by default, it is '_version'.
    This table is created in all version-controlled databases.
    """
    try:
        rep=cls_repository.create(repository,name,**opts)
    except exceptions.PathFoundError,e:
        raise exceptions.KnownError("The path %s already exists"%e.args[0])

def script(description,repository=None,**opts):
    """%prog script [--repository=REPOSITORY_PATH] DESCRIPTION

    Create an empty change script using the next unused version number appended with the given description.
    For instance, manage.py script "Add initial tables" creates: repository/versions/001_Add_initial_tables.py
    """
    try:
        if repository is None:
            raise exceptions.UsageError("A repository must be specified")
        repos = cls_repository(repository)
        repos.create_script(description,**opts)
    except exceptions.PathFoundError,e:
        raise exceptions.KnownError("The path %s already exists"%e.args[0])

def script_sql(database,repository=None,**opts):
    """%prog script_sql [--repository=REPOSITORY_PATH] DATABASE

    Create empty change SQL scripts for given DATABASE, where DATABASE is either specific ('postgres', 'mysql',
    'oracle', 'sqlite', etc.) or generic ('default').
    For instance, manage.py script_sql postgres creates:
    repository/versions/001_upgrade_postgres.py and repository/versions/001_downgrade_postgres.py
    """
    try:
        if repository is None:
            raise exceptions.UsageError("A repository must be specified")
        repos = cls_repository(repository)
        repos.create_script_sql(database,**opts)
    except exceptions.PathFoundError,e:
        raise exceptions.KnownError("The path %s already exists"%e.args[0])

def test(repository,url=None,**opts):
    """%prog test REPOSITORY_PATH URL [VERSION]
    """
    engine=create_engine(url)
    repos=cls_repository(repository)
    script = repos.version(None).script()
    # Upgrade
    print "Upgrading...",
    try:
        script.run(engine,1)
    except:
        print "ERROR"
        raise
    print "done"

    print "Downgrading...",
    try:
        script.run(engine,-1)
    except:
        print "ERROR"
        raise
    print "done"
    print "Success"

def version(repository,**opts):
    """%prog version REPOSITORY_PATH

    Display the latest version available in a repository.
    """
    repos=cls_repository(repository)
    return repos.latest

def source(version,dest=None,repository=None,**opts):
    """%prog source VERSION [DESTINATION] --repository=REPOSITORY_PATH

    Display the Python code for a particular version in this repository.
    Save it to the file at DESTINATION or, if omitted, send to stdout. 
    """
    if repository is None:
        raise exceptions.UsageError("A repository must be specified")
    repos=cls_repository(repository)
    ret=repos.version(version).script().source()
    if dest is not None:
        dest=open(dest,'w')
        dest.write(ret)
        ret=None
    return ret

def version_control(url,repository,version=None,**opts):
    """%prog version_control URL REPOSITORY_PATH [VERSION]

    Mark a database as under this repository's version control.
    Once a database is under version control, schema changes should only be
    done via change scripts in this repository. 

    This creates the table version_table in the database.

    The url should be any valid SQLAlchemy connection string.

    By default, the database begins at version 0 and is assumed to be empty.
    If the database is not empty, you may specify a version at which to begin
    instead. No attempt is made to verify this version's correctness - the
    database schema is expected to be identical to what it would be if the
    database were created from scratch. 
    """
    engine=create_engine(url)
    cls_schema.create(engine,repository,version)

def db_version(url,repository,**opts):
    """%prog db_version URL REPOSITORY_PATH

    Show the current version of the repository with the given connection
    string, under version control of the specified repository. 

    The url should be any valid SQLAlchemy connection string.
    """
    engine = create_engine(url)
    schema = cls_schema(engine,repository)
    return schema.version

def upgrade(url,repository,version=None,**opts):
    """%prog upgrade URL REPOSITORY_PATH [VERSION] [--preview_py|--preview_sql]

    Upgrade a database to a later version. 
    This runs the upgrade() function defined in your change scripts.

    By default, the database is updated to the latest available version. You
    may specify a version instead, if you wish.

    You may preview the Python or SQL code to be executed, rather than actually
    executing it, using the appropriate 'preview' option.
    """
    err = "Cannot upgrade a database of version %s to version %s. "\
        "Try 'downgrade' instead."
    return _migrate(url,repository,version,upgrade=True,err=err,**opts)

def downgrade(url,repository,version,**opts):
    """%prog downgrade URL REPOSITORY_PATH VERSION [--preview_py|--preview_sql]

    Downgrade a database to an earlier version.
    This is the reverse of upgrade; this runs the downgrade() function defined
    in your change scripts.

    You may preview the Python or SQL code to be executed, rather than actually
    executing it, using the appropriate 'preview' option.
    """
    err = "Cannot downgrade a database of version %s to version %s. "\
        "Try 'upgrade' instead."
    return _migrate(url,repository,version,upgrade=False,err=err,**opts)

def _migrate(url,repository,version,upgrade,err,**opts):
    engine = create_engine(url)
    schema = cls_schema(engine,repository)
    version = _migrate_version(schema,version,upgrade,err)

    changeset = schema.changeset(version)
    for ver,change in changeset:
        nextver = ver + changeset.step
        print '%s -> %s... '%(ver,nextver),
        if opts.get('preview_sql'):
            print
            print change.log
        elif opts.get('preview_py'):
            source_ver = max(ver,nextver)
            module = schema.repository.version(source_ver).script().module
            funcname = upgrade and "upgrade" or "downgrade"
            func = getattr(module,funcname)
            print
            print inspect.getsource(module.upgrade)
        else:
            schema.runchange(ver,change,changeset.step)
            print 'done'

def _migrate_version(schema,version,upgrade,err):
    if version is None:
        return version
    # Version is specified: ensure we're upgrading in the right direction
    # (current version < target version for upgrading; reverse for down)
    version = cls_vernum(version)
    cur = schema.version
    if upgrade is not None:
        if upgrade:
            direction = cur <= version
        else:
            direction = cur >= version
        if not direction:
            raise exceptions.KnownError(err%(cur,version))
    return version

def drop_version_control(url,repository,**opts):
    """%prog drop_version_control URL REPOSITORY_PATH

    Removes version control from a database.
    """
    engine=create_engine(url)
    schema=cls_schema(engine,repository)
    schema.drop()

def manage(file,**opts):
    """%prog manage FILENAME VARIABLES...

    Creates a script that runs Migrate with a set of default values. 

    For example::

        %prog manage manage.py --repository=/path/to/repository --url=sqlite:///project.db

    would create the script manage.py. The following two commands would then
    have exactly the same results::

        python manage.py version
        %prog version --repository=/path/to/repository
    """
    return repository.manage(file,**opts)

def compare_model_to_db(url,model,repository,**opts):
    """%prog compare_model_to_db URL MODEL REPOSITORY_PATH

    Compare the current model (assumed to be a module level variable of type sqlalchemy.MetaData) against the current database.

    NOTE: This is EXPERIMENTAL.
    """  # TODO: get rid of EXPERIMENTAL label
    engine=create_engine(url)
    print cls_schema.compare_model_to_db(engine,model,repository)

def create_model(url,repository,**opts):
    """%prog create_model URL REPOSITORY_PATH

    Dump the current database as a Python model to stdout.

    NOTE: This is EXPERIMENTAL.
    """  # TODO: get rid of EXPERIMENTAL label
    engine=create_engine(url)
    print cls_schema.create_model(engine,repository)

def make_update_script_for_model(url,oldmodel,model,repository,**opts):
    """%prog make_update_script_for_model URL OLDMODEL MODEL REPOSITORY_PATH

    Create a script changing the old Python model to the new (current) Python model, sending to stdout.

    NOTE: This is EXPERIMENTAL.
    """  # TODO: get rid of EXPERIMENTAL label
    engine=create_engine(url)
    try:
        print cls_script_python.make_update_script_for_model(engine,oldmodel,model,repository,**opts)
    except exceptions.PathFoundError,e:
        raise exceptions.KnownError("The path %s already exists"%e.args[0])  # TODO: get rid of this? if we don't add back path param

def update_db_from_model(url,model,repository,**opts):
    """%prog update_db_from_model URL MODEL REPOSITORY_PATH

    Modify the database to match the structure of the current Python model.
    This also sets the db_version number to the latest in the repository.

    NOTE: This is EXPERIMENTAL.
    """  # TODO: get rid of EXPERIMENTAL label
    engine=create_engine(url)
    schema = cls_schema(engine,repository)
    schema.update_db_from_model(model)

