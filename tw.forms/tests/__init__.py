import os
import pkg_resources

pkg_resources.require('Genshi')

import tw.api
from tw.core.testutil import get_doctest_suite

dist_base = pkg_resources.get_distribution('tw.forms').location

DOCTEST_FILES = [
    os.path.join(dist_base, 'tests', 'test_*.txt'),
    ]

DOCTEST_MODULES = [
    "tw.forms.core",
    "tw.forms.fields",
    "tw.forms.datagrid",
    "tw.forms.calendars",
    "tw.forms.validators",
    ]

def additional_tests():
    return get_doctest_suite(DOCTEST_FILES, DOCTEST_MODULES)
