import unittest
import aptly_importer


#class TestConfigBase(unittest.TestCase):
#    def setUp(self):
#        self.config = repository.load_config_file('config/_test_repository.yaml')
# sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
# sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 871920D1991BC93C
#http://packages.osrfoundation.org/gazebo/ubuntu

class TestYamlConfiguration(unittest.TestCase):
    def test_non_existing_file(self):
        with self.assertRaises(SystemExit):
            aptly_importer.UpdaterConfiguration('test/i_do_not_exist.yaml')

    def test_missing_field(self):
        with self.assertRaises(SystemExit):
            aptly_importer.UpdaterConfiguration('test/missing_architectures_field.yaml')

    def test_ok(self):
        self.assertTrue(aptly_importer.UpdaterConfiguration('test/example.yaml'))


class TestAptly(unittest.TestCase):
    def setUp(self):
        self.aptly = aptly_importer.Aptly()

    def test_aptly_installed(self):
        self.assertTrue(self.aptly.run(['version']))

    def test_valid_filter(self):
        self.assertTrue(self.aptly.check_valid_filter('mysql-client (>= 3.6)'))

    def test_invalid_filter(self):
        self.assertFalse(self.aptly.check_valid_filter('mysql-client (>= 3.6'))

    def tets_invalid_mirror(self):
        self.assertFalse(self.aptly.check_mirror_exists('i_do_not_exist'))


class TestUpdaterManager(unittest.TestCase):
    def setUp(self):
        self.aptly = aptly_importer.Aptly()
        self.expected_mirror_test_name = '_reprepro_updater_test_suite_-focal'

    def _remove_mirror(self, mirror_name):
        self.aptly.run(['mirror', 'drop', mirror_name], show_errors=False, fail_on_errors=False)

    def test_example_creation(self):
        self._remove_mirror(self.expected_mirror_test_name)
        manager = aptly_importer.UpdaterManager('test/example.yaml')
        manager.run()
        self.assertTrue(self.aptly.check_mirror_exists(self.expected_mirror_test_name))
        self._remove_mirror(self.expected_mirror_test_name)


class TestReprepro2AptlyFilter(unittest.TestCase):
    def setUp(self):
        self.aptly = aptly_importer.Aptly()
        self.filter = aptly_importer.Reprepro2AptlyFilter()

    def _assert_valid_filter(self, filter_str):
        self.assertTrue(self.aptly.check_valid_filter(
            self.filter.convert(filter_str)))

    def test_package(self):
        self._assert_valid_filter('Package (% sdformat)')

    def test_package_version(self):
        self._assert_valid_filter('Package (% sdformat*), $Version (>= 6.2.0+dfsg-2build1)')

    def test_multi_package_version(self):
        filter_formula = """ \
        ((Package (% =lark-parser) |\
          Package (% =python3-lark-parser) |\
          Package (% =python3-lark-parser-doc)),
          $Version (% 0.7.2-3osrf~* ))\
        """
        self._assert_valid_filter(filter_formula)


if __name__ == '__main__':
    unittest.main()
