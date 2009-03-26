try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

version = '0.6.2'

setup(
    name="WebHelpers",
    version=version,
    description='Web Helpers',
    long_description="""
Web Helpers is a library of helper functions intended to make writing 
templates in web applications easier. 

One of the sub-sections of Web Helpers contains a full port of the 
template helpers that are provided by Ruby on Rails with slight 
adaptations on occasion to accomodate for Python.

A few of these helpers require `Routes <http://routes.groovie.org/>`_ 
to function.

* `Development svn <http://pylonshq.com/svn/WebHelpers/trunk#egg=WebHelpers-dev>`_

""",
    author='Mike Orr, Ben Bangert, Phil Jenvey',
    author_email='sluggoster@gmail.com, ben@groovie.org, pjenvey@groovie.org',
    url='http://pylonshq.com/WebHelpers/',
    packages=find_packages(exclude=['ez_setup']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        ],
    tests_require=[ 
      'nose',
      'routes'
      ], 
    test_suite='nose.collector',
    classifiers=["Development Status :: 4 - Beta",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: BSD License",
                 "Programming Language :: Python",
                 "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
                 "Topic :: Software Development :: Libraries :: Python Modules",
               ],
    entry_points="""
    [buildutils.optional_commands]
    compress_resources = webhelpers.commands
    """,
)
