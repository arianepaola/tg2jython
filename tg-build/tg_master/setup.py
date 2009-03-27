from setuptools import setup, find_packages
setup(
    name = "TG_Master",
    version = "0.1.0.2",
    packages = ["tg_master"],
    author = "Steven Mohr",
    author_email = "opensource@stevenmohr.de",
    description = "This package contains some builders and functions used by\
    TurboGears' BuildBot. It also contains the server-side representation of\
    the build steps included in the tg_buildbot_extensions package.",
    license = "MIT",
    keywords = "BuildBot TurboGears extensions",
    url = "http://code.google.com/p/tg-buildbot-extensions/",
)
