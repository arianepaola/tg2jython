import os
import pkg_resources

import tw.api
from tw.core.testutil import get_doctest_suite

dist_base = pkg_resources.get_distribution('ToscaWidgets').location

DOCTEST_FILES = [
    os.path.join(dist_base, 'docs', '*.txt'),
    os.path.join(dist_base, 'tests', 'test_*.txt'),
    os.path.join(dist_base, 'README.txt'),
    ]

DOCTEST_MODULES = [
    "tw.core.base",
    "tw.core.meta",
    "tw.core.util",
    "tw.core.resources",
    "tw.core.resource_injector",
    "tw.core.view",
    "tw.core.js",
    ]

def additional_tests():
    return get_doctest_suite(DOCTEST_FILES, DOCTEST_MODULES)
