#setup.py
from setuptools import setup, find_packages

setup(
  name="DBSprockets",
  version="0.2",
  zip_safe=False,
  include_package_data=True,
  description="""A package for creation of web widgets directly from database definitions.""",
  author="Christopher Perkins 2007",
  author_email="chris@percious.com",
  license="MIT",
  url="http://dbsprockets.googlecode.com/svn/dist",
  install_requires=['sqlalchemy>=0.4',
                    'tw.forms>=0.8',
                    #'Genshi>=0.4',
                    ],
  packages = find_packages(),
  classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
 entry_points = """[toscawidgets.widgets]
        # Use 'widgets' to point to the module where widgets should be imported
        # from to register in the widget browser
        widgets = dbsprockets.widgets
        # Use 'samples' to point to the module where widget examples
        # should be imported from to register in the widget browser
        # samples = tw.samples
        # Use 'resources' to point to the module where resources
        # should be imported from to register in the widget browser
        #resources = dbsprockets.widgets.resources
       """
#  entry_points="""
#        [paste.paster_create_template]
#        dbsprockets=dbsprockets.instance.newDBSprockets:Template
#    """,

  )
