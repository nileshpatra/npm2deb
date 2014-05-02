import sys
import os
import inspect
current = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe()) + '/..'))
sys.path.append(current)

import unittest
from commands import getstatusoutput
from shutil import rmtree
from npm2deb import Npm2Deb, DEBHELPER


class npm2deb_fails(unittest.TestCase):
    def test_init_no_npm_module(self):
        try:
            n = Npm2Deb('MODULE_NOT_IN_NPM')
            raise Exception
        except Exception as err:
            self.assertTrue(isinstance(err, ValueError))
            # must suggest type of failure
            self.assertTrue(str(err).find('npm reports errors about') >= 0)

    def test_init_module_multiple_version(self):
        try:
            n = Npm2Deb('socket.io@0.9.x')
            raise Exception
        except Exception as err:
            self.assertTrue(isinstance(err, ValueError))
            # must suggest type of failure
            self.assertTrue(str(err).find(\
                'More than one version found. Please specify one of:') >= 0)


class npm_coherences_license(unittest.TestCase):

    def test_upstream_license_as_str(self):
        n = Npm2Deb('parse-url')
        self.assertEqual(n.upstream_license, 'Expat')

    def test_upstream_license_as_dict(self):
        n = Npm2Deb('utils-merge')
        self.assertEqual(n.upstream_license, 'Expat')

    def test_upstream_license_as_list(self):
        n = Npm2Deb('amdefine')
        self.assertEqual(n.upstream_license, 'BSD')

    def test_upstream_license_as_argument(self):
        n = Npm2Deb('amdefine', {'upstream_license': 'MIT'})
        self.assertEqual(n.upstream_license, 'MIT')

    def test_upstream_license_equals_debian_license(self):
        n = Npm2Deb('parse-url')
        self.assertEqual(n.upstream_license, n.debian_license)

    def test_debian_license_as_argument(self):
        n = Npm2Deb('amdefine', {'debian_license': 'GPL-3'})
        self.assertEqual(n.debian_license, 'GPL-3')


class debian(unittest.TestCase):

    def _get_compat(self):
        with open('debian/compat', 'r') as compat_fd:
            return compat_fd.read().strip('\n')

    def _get_control_field(self, what):
        result = None
        with open('debian/control', 'r') as control:
            for line in control.readlines():
                if line.find(what) >= 0:
                    result = line.strip('\n')
                    break
        return result

    def test_debhelper(self):
        n = Npm2Deb('parse-url')
        n.create_base_debian()
        n.create_control()
        self.assertEqual(self._get_compat(), str(DEBHELPER))
        self.assertEqual(self._get_control_field(" debhelper ("),\
            ' debhelper (>= %s)' % DEBHELPER)

    def test_debhelper_as_argument(self):
        MY_DEBHELPER = DEBHELPER + 1
        n = Npm2Deb('parse-url', {'debhelper': MY_DEBHELPER})
        n.create_base_debian()
        n.create_control()
        self.assertEqual(self._get_compat(), str(MY_DEBHELPER))
        self.assertEqual(self._get_control_field(" debhelper ("),\
            ' debhelper (>= %s)' % MY_DEBHELPER)

    def tearDown(self):
        if os.path.isdir('debian'):
            rmtree('debian')

if __name__ == '__main__':
    unittest.main()