import testenv; testenv.configure_for_tests()
import unittest

def suite():
    modules_to_test = (
        # core utilities
        'base.dependency',
        'base.utils',
        'base.except',
        )
    alltests = unittest.TestSuite()
    for name in modules_to_test:
        mod = __import__(name)
        for token in name.split('.')[1:]:
            mod = getattr(mod, token)
        alltests.addTest(unittest.findTestCases(mod, suiteClass=None))
    return alltests


if __name__ == '__main__':
    testenv.main(suite())
