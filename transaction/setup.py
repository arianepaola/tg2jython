##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__version__ = '1.0a1'

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = (open(os.path.join(here, 'README.txt')).read()
          + '\n\n' +
          open(os.path.join(here, 'CHANGES.txt')).read())

setup(name='transaction',
      version=__version__,
      description='Transaction management for Python',
      long_description=README,
      classifiers=[
        "Development Status :: 6 - Mature",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        ],
      author="Zope Corporation",
      author_email="zodb-dev@zope.org",
      url="http://www.zope.org/Products/ZODB",
      license="ZPL 2.1",
      platforms=["any"],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite="transaction.tests",
      tests_require = [
        'zope.interface',
        'zope.testing',
        ],
      install_requires=[
        'zope.interface',
        ],
      entry_points = """\
      """
      )

