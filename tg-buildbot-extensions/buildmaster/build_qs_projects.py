#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""A script which calls tg-admin with every possible combination of Identity enabled/disabled, SQLObject/SQLAlchemy/Elixir and Kid/Genshi."""


__program__   = "build_qs_projects.py"
__author__    = "Steven Mohr"
__version__   = "0.1"
__revision__  = "$Rev:$"
__date__      = "$Date:$"
__copyright__ = "MIT license"

import os
import sys
from subprocess import call, Popen, PIPE, STDOUT


# tg-admin quickstart options
identity = dict(
    no_identity = '',
    identity = '-i',
)

sql = dict(
    elixir = '-e',
    sqlobject = '-o',
    sqlalchemy = '-s',
)

template = dict(
    kid = '',
    genshi = '--template=tggenshi',
)


def run_quickstart(cmdline):
    """Run 'tg-admin quickstart' with given command line."""

    cmdline = ["tg-admin", "quickstart"] + cmdline
    # for debugging
    print " ".join(cmdline)
    if "-i" not in cmdline:
        p = Popen(cmdline, shell=False, env=os.environ,
            stdin=PIPE, stderr=STDOUT, stdout=PIPE, close_fds=True)
        print p.communicate("n\n")[0]
        return p.wait()
    else:
        return call(cmdline, shell=False, close_fds=True, env=os.environ,)

def main(args):
    for idtype, idval in identity.items():
        for ormtype, ormval in sql.items():
            for tmpltype, tmplval in template.items():
                project_name = "qs_%s_%s_%s" % (idtype, ormtype, tmpltype)
                pkg_name = "qstest"
                cmdline = [ormval, "--package=%s" % pkg_name, project_name]
                if idval:
                    cmdline.insert(0, idval)
                if tmplval:
                    cmdline.insert(0, tmplval)
                # XXX do something with retcode
                retcode = run_quickstart(cmdline)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
