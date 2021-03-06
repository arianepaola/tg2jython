import testenv; testenv.configure_for_tests()
from testlib import sa_unittest as unittest

def suite():
    modules_to_test = (
        'orm.inheritance.basic',
        'orm.inheritance.query',
        'orm.inheritance.manytomany',
        'orm.inheritance.single',
        'orm.inheritance.concrete',
        'orm.inheritance.polymorph',
        'orm.inheritance.polymorph2',
        'orm.inheritance.poly_linked_list',
        'orm.inheritance.abc_polymorphic',
        'orm.inheritance.abc_inheritance',
        'orm.inheritance.productspec',
        'orm.inheritance.magazine',
        'orm.inheritance.selects',

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
