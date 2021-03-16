import argparse
from pathlib import Path
from os import path
from subprocess import PIPE, run, CalledProcessError
from sys import stderr
import yaml


class Reprepro2AptlyFilter():
    def convert(self, filter_str):
        # remove begin/end whitespaces
        r_str = filter_str.lstrip()
        # Package menas nothing as filter. Could be Name or empty.
        r_str = r_str.replace('Package', 'Name')
        # Do not use equal symbols, just remove
        r_str = r_str.replace('% =', '')
        return r_str


class Aptly():
    def run(self, cmd=[], fail_on_errors=True, show_errors=True):
        run_cmd = ['aptly'] + cmd
        # print(f"RUN {' '.join(run_cmd)}")
        try:
            r = run(run_cmd, stdout=PIPE, stderr=PIPE)
        except CalledProcessError as e:
            return False
        if r.returncode == 0:
            return True
        else:
            if show_errors:
                self.__error(run_cmd, f"{r.stderr.decode('utf-8')}", fail_on_errors)
            return False

    def check_valid_filter(self, filter_str):
        fake_mirror_name = '_test_aptly_filter'
        create_mirror_cmd = ['mirror', 'create',
                             f"-filter={filter_str}",
                             fake_mirror_name,
                             'http://deb.debian.org/debian', 'sid', 'main']
        result = self.run(create_mirror_cmd, fail_on_errors=False)
        if not result:
            return result
        delete_mirror_cmd = ['mirror', 'drop', fake_mirror_name]
        self.run(delete_mirror_cmd)
        return True

    def check_mirror_exists(self, mirror_name):
        return self.run(['mirror', 'show', mirror_name],
                        fail_on_errors=False, show_errors=False)

    def check_repo_exists(self, repo_name):
        return self.run(['repo', 'show', repo_name],
                        fail_on_errors=False, show_errors=False)

    def __error(self, cmd, msg, exit=False):
        print(f"Aptly error running: {cmd} \n", file=stderr)
        print(f"{msg} \n", file=stderr)


class UpdaterConfiguration():
    def __init__(self, input_file):
        try:
            self.config = self.load_config_file(input_file)
            self.reprepro2aptly = Reprepro2AptlyFilter()

            self.architectures = self.config['architectures']
            # source was accepted as a valid architecture to indicate that
            # source packages need to be download. It is not a valid arch in aptly
            if 'source' in self.config['architectures']:
                self.architectures = self.config['architectures'].remove('source')
            self.architectures = self.config['architectures']
            self.component = self.config['component']
            self.filter_formula = self.reprepro2aptly.convert(
                self.config['filter_formula'])
            self.method = self.config['method']
            self.name = self.config['name']
            self.suites = self.config['suites']
        except KeyError as e:
            self.error(f"{e} key was not found in file {input_file}")

    def load_config_file(self, config_file_path):
        fn = Path(__file__).parent / config_file_path
        try:
            with open(str(fn), 'r') as stream:
                config = yaml.safe_load(stream)
                return config
        except yaml.YAMLError as exc:
            self.error(f"yaml parsing error {exc}")
        except FileNotFoundError as e:
            self.error(f"not found {config_file_path}")

    def error(self, msg):
        print(f"Configuration file error: {msg} \n", file=stderr)
        exit(-1)


class UpdaterManager():
    def __init__(self, input_file):
        self.config = UpdaterConfiguration(input_file)
        self.aptly = Aptly()

    def __create_aptly_mirror(self, distribution):
        assert(self.config)
        mirror_name = self.__get_mirror_name(distribution)
        self.aptly.run(['mirror', 'create', '-with-sources',
                        f"-architectures={','.join(self.config.architectures)}",
                        f"-filter={self.config.filter_formula}",
                        mirror_name,
                        self.config.method,
                        distribution,
                        self.config.component])
        self.aptly.run(['mirror', 'update', mirror_name])

    def __error(self, msg):
        print(f"Update Manager error: {msg} \n", file=stderr)
        exit(-1)

    def __get_mirror_name(self, distribution):
        return f"{self.config.name}-{distribution}"

    def __get_repo_name(self, distribution):
        return f"ros_bootstrap-{distribution}"

    def __import__aptly_mirror_to_repo(self, distribution):
        repo_name = self.__get_repo_name(distribution)
        # create repository if it does not exist. New distribution probably
        if not self.aptly.check_repo_exists(repo_name):
            self.aptly.run(['repo', 'create', repo_name])
        self.aptly.run(['repo', 'import',
                        self.__get_mirror_name(distribution),
                        repo_name,
                        self.config.filter_formula])

    def assure_aptly_mirrors_do_not_exist(self):
        for dist in self.config.suites:
            mirror_name = self.__get_mirror_name(dist)
            if self.aptly.check_mirror_exists(mirror_name):
                self.__error(f"mirror {mirror_name} exists. Refuse to create mirrors")

    def run(self):
        # 1. Create aptly mirrors from yaml configuration file
        # check aptly mirrors before creating to avoid problems beforehand
        self.assure_aptly_mirrors_do_not_exist()
        for dist in self.config.suites:
            self.__create_aptly_mirror(dist)
            # 2. Import from mirrors to local repositories
            self.__import__aptly_mirror_to_repo(dist)


def main():
    """
    Usage: python3 aptly_importer.py <config_file>
    Output: list of added/removed/versioned packages
    """
    usage = "usage: %prog config_file"
    parser = argparse.ArgumentParser(usage)
    parser.add_argument('config_file', type=str, nargs='+', default=None)

    args = parser.parse_args()

    if not path.exists(args.config_file[0]):
        parser.error("Missing input file from %s" % args.config_file[0])

    manager = UpdaterManager(args.config_file[0])
    manager.run()


if __name__ == '__main__':
    main()
