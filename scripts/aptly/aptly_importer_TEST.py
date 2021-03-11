import unittest
import aptly_importer


#class TestConfigBase(unittest.TestCase):
#    def setUp(self):
#        self.config = repository.load_config_file('config/_test_repository.yaml')


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


if __name__ == '__main__':
    unittest.main()
