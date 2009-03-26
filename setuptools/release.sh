#!/bin/sh

# This script is for PJE's working environment only, to upload
# releases to PyPI, telecommunity, eby-sarna SVN, update local
# project checkouts, etc.
#
# If your initials aren't PJE, don't run it.  :)
#

export VERSION="0.6c8"

python2.3 setup.py -q release source --target-version=2.3 upload && \
python2.4 setup.py -q release binary --target-version=2.4 upload && \
python2.5 setup.py -q release binary --target-version=2.5 upload && \
python2.3 ez_setup.py --md5update dist/setuptools-$VERSION*-py2.?.egg && \
  cp ez_setup.py virtual-python.py ~/distrib/ && \
  cp ez_setup.py ~/projects/ez_setup/__init__.py && \
  svn ci -m "Update ez_setup for setuptools $VERSION" \
      ~/projects/ez_setup/__init__.py #&& \
  #svn up ~/projects/*/ez_setup

# XXX update wiki pages
#
#./wikiup setuptools setuptools.txt 
#./wikiup PkgResources pkg_resources.txt 
#./wikiup EasyInstall EasyInstall.txt 
