import aptly_importer
import os
import sys
import tempfile
import unittest

class TestYamlConfiguration(unittest.TestCase):
    def test_non_existsing_file(self):
        with self.assertRaises(SystemExit):
            aptly_importer.UpdaterConfiguration('test/i_do_not_exists.yaml')

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
        self.assertFalse(self.aptly.check_mirror_exists('i_do_not_exists'))


class TestUpdaterManager(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile(dir='/tmp', delete=False) as tmpfile:
            tmpfile.write("""\
            {
              "downloadSourcePackages": true,
              "gpgDisableSign": false,
              "FileSystemPublishEndpoints": {
                "live": {
                  "rootDir": "/tmp/reprepro_updater/"
                }
              }
            }""".encode())
            self.aptly_config_file = tmpfile.name

        self.aptly = aptly_importer.Aptly(config_file=self.aptly_config_file)
        self.debug_msgs =\
            os.environ['_DEBUG_MSGS_REPREPRO_UPDATER_TEST_SUITE_'] if '_DEBUG_MSGS_REPREPRO_UPDATER_TEST_SUITE_' in os.environ else False

    def tearDown(self):
        self.__clean_up_aptly_test_artifacts()
        if os.path.exists(self.aptly_config_file):
            os.remove(self.aptly_config_file)
        else:
            assert(False), f"{self.aptly_config_file} file does not exist while trying to remove it"

    def __add_repo(self, repo_name):
        self.assertTrue(self.aptly.run(['repo', 'create', repo_name]))

    def __assert_no_mirrors(self):
        for name in self.expected_mirrors_test_name:
            self.assertFalse(self.aptly.exists(aptly_importer.Aptly.ArtifactType.MIRROR,
                                               name))

    def __assert_expected_repos_mirrors(self):
        for name in self.expected_mirrors_test_name:
            self.assertTrue(self.aptly.exists(aptly_importer.Aptly.ArtifactType.MIRROR,
                                              name))
            self.assertGreater(
                self.aptly.get_number_of_packages(aptly_importer.Aptly.ArtifactType.MIRROR,
                                                  name),
                0)
        for name in self.expected_repos_test_name:
            self.assertTrue(self.aptly.exists(aptly_importer.Aptly.ArtifactType.REPOSITORY,
                                              name))

    def __clean_up_aptly_test_artifacts(self):
        [self.__remove_publish(dist) for dist in self.expected_distros]
        [self.__remove_repo(name) for name in self.expected_repos_test_name]
        [self.__remove_mirror(name) for name in self.expected_mirrors_test_name]
        [self.__remove_snapshots_from_mirror(name) for name in self.expected_mirrors_test_name]
        self.aptly.run(['db', 'cleanup'])

    def __remove_mirror(self, mirror_name):
        self.aptly.run(['mirror', 'drop', '-force', mirror_name],
                       show_errors=False, fail_on_errors=False)

    def __remove_publish(self, distro):
        self.aptly.run(['publish', 'drop',
                       f"-config={self.aptly_config_file}",
                       distro,
                       self.expected_endpoint_name],
                       show_errors=False, fail_on_errors=False)

    def __remove_repo(self, repo_name):
        # be sure to unpublish the repo otherwise can not be removed
        self.aptly.run(['repo', 'drop', '-force', repo_name],
                       show_errors=False, fail_on_errors=False)

    def __remove_snapshots_from_mirror(self, mirror_name):
        for snap in self.aptly.get_snapshots_from_mirror(mirror_name):
            self.aptly.run(['snapshot', 'drop', snap])

    def __setup__(self, distros_expected):
        self.expected_distros = distros_expected
        self.expected_endpoint_name = 'filesystem:live:ros_bootstrap'
        self.expected_mirrors_test_name = [f"_reprepro_updater_test_suite_-{distro}"
                                           for distro in self.expected_distros]
        self.expected_repos_test_name = [f"ros_bootstrap-{distro}"
                                         for distro in self.expected_distros]
        self.expected_repos_by_distro_test_name =\
            {f"{distro}": f"ros_bootstrap-{distro}" for distro in self.expected_distros}

        # clean up testing artifacts if they previously exists
        self.__clean_up_aptly_test_artifacts()

    def test_basic_example_creation_from_scratch(self):
        self.__setup__(['focal', 'groovy'])
        manager = aptly_importer.UpdaterManager('test/example.yaml',
                                                debug=self.debug_msgs,
                                                aptly_config_file=self.aptly_config_file)
        self.assertTrue(manager.run())
        self.__assert_expected_repos_mirrors()

    def test_basic_example_creation_existing_repo(self):
        self.__setup__(['focal', 'groovy'])
        [self.__add_repo(name) for name in self.expected_repos_test_name]
        manager = aptly_importer.UpdaterManager('test/example.yaml',
                                                aptly_config_file=self.aptly_config_file)
        self.assertTrue(manager.run())
        self.__assert_expected_repos_mirrors()

    def test_example_no_sources(self):
        self.__setup__(['xenial'])
        manager = aptly_importer.UpdaterManager('test/example_no_source_package.yaml',
                                                aptly_config_file=self.aptly_config_file)
        with self.assertRaises(SystemExit):
            manager.run()
        self.__assert_no_mirrors()


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
    aptly = aptly_importer.Aptly()
    # test suite is potentially dangerous for production machines
    if os.getenv('_ALLOW_DESTRUCTIVE_TESTS_REPREPRO_UPDATER_TEST_SUITE_') and \
       os.environ['_ALLOW_DESTRUCTIVE_TESTS_REPREPRO_UPDATER_TEST_SUITE_']:
            print("_ALLOW_DESTRUCTIVE_TESTS_REPREPRO_UPDATER_TEST_SUITE_ variable is"
                  "not set to true. Refuse to run test suite")
            sys.exit(2)
    unittest.main()
