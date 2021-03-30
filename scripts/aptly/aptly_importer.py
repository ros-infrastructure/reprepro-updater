import argparse
from collections import defaultdict
from enum import Enum
from pathlib import Path
from os import path
from subprocess import check_output, PIPE, run, CalledProcessError
from sys import stderr, exit
import re
import time
import yaml


class Reprepro2AptlyFilter():
    def convert(self, filter_str):
        # remove begin/end whitespaces
        r_str = filter_str.strip()
        # Package is not a valid Aptly filter. Could be Name or empty.
        r_str = r_str.replace('Package', 'Name')
        # Aptly filters use (= value) for exact matches rather than (% =value)
        r_str = r_str.replace('% =', '= ')
        return r_str


class Aptly():
    class ArtifactType(Enum):
            MIRROR = 'mirror'
            REPOSITORY = 'repo'
            SNAPSHOT = 'snapshot'
            PUBLISH = 'publish'

    def __init__(self, debug=False, config_file=None):
        self.debug = debug
        self.config_file = config_file

    def __error(self, cmd, msg, exit_on_errors=False):
        print(f"Aptly error running: {cmd}", file=stderr)
        print(f"  --> {msg} \n", file=stderr)
        if exit_on_errors:
            exit(1)

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

    def exists(self, aptly_type: ArtifactType, name):
        assert(aptly_type != Aptly.ArtifactType.PUBLISH), 'PUBLISH uses exists_publication'
        return self.run([aptly_type.value, 'show', name],
                        fail_on_errors=False, show_errors=False)

    def exists_all_source_packages(self, aptly_type: ArtifactType, name):
        if not self.exists(aptly_type, name):
            self.__error('exists_all_source_packages method',
                         f"{aptly_type.value} does not exist")
            return False

        packages_by_source = self.get_packages_by_source_package(aptly_type, name)
        source_packages = self.get_source_packages(aptly_type, name)

        result = True
        for source in packages_by_source:
            if source not in source_packages:
                print(f"Source package '{source}' is missing for packages: "
                      f"{', '.join(packages_by_source[source])}")
                result = False
        return result

    def exists_publication(self, distribution, end_point):
        return self.run(['publish', 'show', distribution, end_point],
                        fail_on_errors=False, show_errors=False)

    def get_number_of_packages(self, aptly_type: ArtifactType, name):
        output = check_output(f"aptly {aptly_type.value} show {name}", shell=True)

        for row in output.splitlines():
            if 'Number of packages' in row.decode():
                return int(row.decode().split(':')[1])
        assert(False), "get_number_of_packages did not found a valid 'Number of packages' line"

    # returns a dictionary with source package as index and deb packages corresponding to
    # that source package as values
    def get_packages_by_source_package(self, aptly_type: ArtifactType, name):
        packages_by_source = defaultdict(set)
        cmd = [aptly_type.value, 'search',
               '-format={{.Package}}::{{.Source}}',
               name,
               '$PackageType (= deb)']
        result = self.run(cmd, return_all_info=True)
        if result.returncode != 0:
            self.__error(cmd, result.stderr.decode('utf-8'), exit_on_errors=True)

        for line in result.stdout.splitlines():
            # ignore empty entries with 'no value'
            if 'no value' in line.decode('utf-8'):
                continue
            package, source = line.decode('utf-8').split('::')
            # Source field may include a parenthesized version which we'll ignore for now.
            # e.g. `pcl (1.11.1+dfsg-1)`
            if len(source.split(' ')) > 1:
                source = source.split(' ')[0]
            packages_by_source[source].add(package)
        return packages_by_source

    def get_source_packages(self, aptly_type, name):
            result = self.run([aptly_type.value, 'search',
                               '-format={{.Package}}',
                               name,
                               '$PackageType (= source)'],
                              return_all_info=True)
            if result.returncode == 0:
                return result.stdout.decode('utf-8').splitlines()
            # handle no source packages scenario
            if 'no results' in result.stderr.decode('utf-8'):
                return []
            else:
                self.__error('get_source_packages method', result.stderr.decode('utf-8'))

    def get_snapshots_from_mirror(self, mirror_name):
        result = []
        output = check_output('aptly snapshot list', shell=True)
        for row in output.splitlines():
            if f"from mirror [{mirror_name}" in row.decode():
                m = re.findall(r"\[(.*)\]: Snapshot", row.decode())
                result.append(m[0])
        return result

    def run(self, cmd=[], fail_on_errors=True, show_errors=True, return_all_info=False):
        run_cmd = ['aptly']
        if self.config_file:
            run_cmd += [f"-config={self.config_file}"]
        run_cmd += cmd
        if self.debug:
            print(f"RUN {' '.join(run_cmd)}")
        try:
            r = run(run_cmd, stdout=PIPE, stderr=PIPE)
        except CalledProcessError as e:
            if return_all_info:
                return r
            return False
        # if return_all_info is enabled return result object
        if return_all_info:
            return r

        if r.returncode == 0:
            return True
        else:
            if show_errors:
                self.__error(run_cmd, f"{r.stderr.decode('utf-8')}", fail_on_errors)
            return False


class UpdaterConfiguration():
    def __init__(self, input_file):
        try:
            self.config = self.__load_config_file(input_file)
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
            self.__error(f"{e} key was not found in file {input_file}")

    def __error(self, msg):
        print(f"Configuration file error: {msg} \n", file=stderr)
        exit(2)

    def __load_config_file(self, config_file_path):
        fn = Path(__file__).parent / config_file_path
        try:
            with open(str(fn), 'r') as stream:
                config = yaml.safe_load(stream)
                return config
        except yaml.YAMLError as exc:
            self.__error(f"yaml parsing error {exc}")
        except FileNotFoundError as e:
            self.__error(f"not found {config_file_path}")


class UpdaterManager():
    def __init__(self, input_file, debug=False, aptly_config_file=None, simulate_repo_import=False, snapshot_and_publish=False):
        self.aptly = Aptly(debug,
                           config_file=aptly_config_file)
        self.config = UpdaterConfiguration(input_file)
        self.debug = debug
        self.simulate_repo_import = simulate_repo_import
        self.snapshot_and_publish = snapshot_and_publish
        self.snapshot_timestamp = None

    def __create_aptly_mirror(self, distribution):
        assert(self.config)
        self.__log(f"Creating aptly mirror for {distribution}")
        mirror_name = self.__get_mirror_name(distribution)
        if self.aptly.exists(Aptly.ArtifactType.MIRROR, mirror_name):
            self.__log_ok('Removing existing mirror')
            self.aptly.run(['mirror', 'drop', mirror_name])
        self.aptly.run(['mirror', 'create', '-with-sources',
                        f"-architectures={','.join(self.config.architectures)}",
                        f"-filter={self.config.filter_formula}",
                        mirror_name,
                        self.config.method,
                        distribution,
                        self.config.component])
        self.aptly.run(['mirror', 'update', mirror_name])
        self.__log_ok(f"mirror {mirror_name} created")

    def __create_aptly_snapshot(self, distribution):
        self.__log('Creating an aptly snapshot from local aptly repository')
        self.aptly.run(['snapshot', 'create', self.__get_snapshot_name(distribution),
                        'from', 'repo', self.__get_repo_name(distribution)])
        self.__log_ok(f"snapshot {self.__get_snapshot_name(distribution)} created from repo {self.__get_repo_name(distribution)}")

    def __error(self, msg):
        print(f"Update Manager error: {msg} \n", file=stderr)
        exit(1)

    def __get_endpoint_name(self, distribution):
        return f"filesystem:live:ros_bootstrap"

    def __get_mirror_name(self, distribution):
        return f"{self.config.name}-{distribution}"

    def __get_repo_name(self, distribution):
        return f"ros_bootstrap-{distribution}"

    def __get_snapshot_name(self, distribution):
        if not self.snapshot_timestamp:
            self.__generate_snapshot_timestamp(distribution)
        return f"{self.__get_repo_name(distribution)}-{self.snapshot_timestamp}"

    def __generate_snapshot_timestamp(self, distribution):
        self.snapshot_timestamp = f"{time.time()}"

    def __import__aptly_mirror_to_repo(self, distribution):
        self.__log('Import aptly mirror into local aptly repo')
        repo_name = self.__get_repo_name(distribution)
        # create repository if it does not exist. New distribution probably
        if not self.aptly.exists(Aptly.ArtifactType.REPOSITORY, repo_name):
            self.aptly.run(['repo', 'create', repo_name])
            self.__log_ok(f"aptly repository {repo_name} was created")
        import_cmd = ['repo', 'import',
                      self.__get_mirror_name(distribution),
                      repo_name,
                      self.config.filter_formula]
        if self.simulate_repo_import:
            import_cmd.insert(2, '-dry-run')

        self.aptly.run(import_cmd)
        self.__log_ok(f"aptly mirror {self.__get_mirror_name(distribution)} imported to the repo {repo_name}")

    def __log(self, msg):
        print(f" {msg} ")

    def __log_ok(self, msg):
        self.__log(f"   [ok] {msg}")

    def __publish_new_snapshot(self, dist):
        self.__log('Publish the new snapshot')
        if (self.aptly.exists_publication(dist, self.__get_endpoint_name(dist))):
            self.aptly.run(['publish', 'switch',
                            dist,
                            self.__get_endpoint_name(dist),
                            self.__get_snapshot_name(dist)])
            self.__log_ok(f"publish switch in {self.__get_endpoint_name(dist)} to use {self.__get_snapshot_name(dist)}")

        else:
            self.aptly.run(['publish', 'snapshot',
                            f"-distribution={dist}",
                            self.__get_snapshot_name(dist),
                            self.__get_endpoint_name(dist)])
            self.__log_ok(f"new publication in {self.__get_endpoint_name(dist)} for {self.__get_snapshot_name(dist)}")

    def __remove_all_generated_mirrors(self):
        for dist in self.config.suites:
            mirror_name = self.__get_mirror_name(dist)
            if self.aptly.exists(Aptly.ArtifactType.MIRROR, mirror_name):
                self.aptly.run(['mirror', 'drop', mirror_name])

    def run(self):
        self.__log(f"\n == [ PROCESSING {self.config.name} ] ==\n")
        for dist in self.config.suites:
            # 1. Create aptly mirrors from yaml configuration file
            self.__create_aptly_mirror(dist)
            # 2. Be sure mirror has all source packages
            self.__log(f'Check all source packages exist')
            if not self.aptly.exists_all_source_packages(Aptly.ArtifactType.MIRROR,
                                                         self.__get_mirror_name(dist)):
                self.__remove_all_generated_mirrors()
                self.__error(f'{self.__get_mirror_name(dist)} does not have a source package. Removing generated mirrors')
            self.__log_ok('There is a source pakage in the mirror')
            # 2. Import from mirrors to local repositories
            self.__import__aptly_mirror_to_repo(dist)
            if self.simulate_repo_import:
                self.__log_ok(f"Simulation of the import actions from mirrors to repos finished")
                exit(0)
            if self.snapshot_and_publish:
                # 3. Create snapshots from repositories
                self.__create_aptly_snapshot(dist)
                # 4. Publish new snapshots
                self.__publish_new_snapshot(dist)
        self.__log(f"\n == [ END OF PROCESSING {self.config.name} ] ==\n")
        return True


def main():
    """
    Usage: python3 aptly_importer.py [--simulate-repo-import] <config_file>
    """
    usage = "usage: %prog [--simulate-repo-import] config_file"
    parser = argparse.ArgumentParser(usage)
    parser.add_argument('config_file', type=str, default=None)
    parser.add_argument('--simulate-repo-import',
                        action='store_true',
                        help='Perform a dry-run until the point of simulation mirrors import to repositories')
    parser.add_argument('--snapshot-and-publish', action='store_true', help='Create and publish a snapshot of the updated distributions')

    args = parser.parse_args()

    if not path.exists(args.config_file):
        parser.error("Missing input file from %s" % args.config_file)

    manager = UpdaterManager(args.config_file, simulate_repo_import=args.simulate_repo_import, snapshot_and_publish=args.snapshot_and_publish)
    manager.run()


if __name__ == '__main__':
    main()
