import imp, unittest, traceback
import os, sys, imp
from optparse import OptionParser
import bauble.pluginmgr as pluginmgr
import testbase


if 'PYTHONPATH' not in os.environ or os.environ['PYTHONPATH'] is '':
    msg = 'This test suite should be run from the top of the source tree '\
          'with the command:\n  PYTHONPATH=. python test/test.py'
    print msg
    sys.exit(1)

# TODO: right now this just runs all tests but should really be able to
# pass individuals tests or test suites on the command line
default_uri = 'sqlite:///:memory:'
parser = OptionParser()
parser.add_option("-c", "--connection", dest="connection", metavar="CONN",
                  default=default_uri, help="connect to CONN")
parser.add_option("-l", "--loglevel", dest='loglevel', metavar='LEVEL (0-61)',
                type='int', default=30, help="display extra test information")


def find_all_tests():
    test_suites = unittest.TestSuite()
    modules = []

    # get all the modules with tests in the test directory that start
    # with test_
    test_path = os.path.join(os.getcwd(), 'test')
    for f in os.listdir(test_path):
        if f.startswith('test_'):
            name, ext = os.path.splitext(f)
            if name not in sys.modules:
                f, path, desc = imp.find_module(name)#, test_path)
                try:
                    modules.append(imp.load_module(name, f, path, desc))
                except ImportError, e:
                    print e


    # get all the plugin test modules
    module_names = pluginmgr._find_module_names(os.getcwd())
    for name in [m for m in module_names if m.startswith('bauble')]:
        try:
            mod = __import__('%s.test' % name, globals(), locals(), [name])
            modules.append(mod)
        except ImportError, e:
            # TODO: this could cause a problem  if there is an ImportError
            # inside the module when importing
##            testbase.log.debug(traceback.format_exc())

            # TODO: this is a bad hack
            if str(e) != 'No module named test': #shouldn't rely on string here
                testbase.log.warning('** ImportError: Could not import '\
                                     '%s.test -- %s' \
                                     % (name, e))

    for mod in modules:
#         tests = test_loader.loadTestsFromModule(mod)
#         if tests.countTestCases() != 0:
#             test_suites.addTest(tests)
        if hasattr(mod, 'testsuite'):
            testbase.log.msg('adding tests from bauble.plugins.%s' %name)
            test_suites.addTest(mod.testsuite())
#            suites.append(mod.testsuite())

    def get_test_cases(suite):
        """
        get all test cases from suite, called recursively
        """
        pass

    return test_suites



if __name__ == '__main__':
    (options, args) = parser.parse_args()
    testbase.log.setLevel(options.loglevel)
    testbase.uri = options.connection
    test_loader = unittest.defaultTestLoader
    if testbase.uri != default_uri:
        print 'uri: %s' % testbase.uri

    global tests
    test_suites = find_all_tests()

    testbase.log.msg('=======================')
    runner = unittest.TextTestRunner()
    if len(args) > 0:
        # run a specific testsuite, would be nice to allow running
        # specific test cases or test methods...
        # unittest.TestLoader().loadTestsFromNames() is a but
        # cumbersome since you have to enter the entire test name like
        # bauble.plugins.garden.test.GardenTestSuite
        test_names = set([t.__class__.__name__ for t in test_suites])
        tn = set([t.__class__.__module__ for t in test_suites])
#        print tn
        not_found = set(args).difference(test_names)
        if len(not_found) != 0:
            raise Exception('Could not find the following tests: %s' % \
                            list(not_found))
        for t in test_suites:
            if t.__class__.__name__ in args:
                runner.run(t)

    else:
        runner.run(test_suites)









