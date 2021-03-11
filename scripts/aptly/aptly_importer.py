import argparse
from pathlib import Path
from os import path
from subprocess import PIPE, run, CalledProcessError
from sys import stderr
import yaml


class Aptly():
    def run(self, cmd=[]):
        run_cmd = ['aptly'] + cmd
        try:
            r = run(run_cmd, stdout=PIPE, stderr=PIPE)
        except CalledProcessError as e:
            print(f"Aptly error: {e.stderr.decode('utf-8')} \n", file=stderr)
            return False
        if r.returncode == 0:
            return True
        else:
            print(f"Aptly error: {r.stderr.decode('utf-8')} \n", file=stderr)
            return False

    def check_valid_filter(self, filter_str):
        fake_mirror_name = '_test_aptly_filter'
        create_mirror_cmd = ['mirror', 'create',
                             f"-filter={filter_str}",
                             fake_mirror_name,
                             'http://deb.debian.org/debian', 'sid', 'main']
        result = self.run(create_mirror_cmd)
        if not result:
            return result
        delete_mirror_cmd = ['mirror', 'drop', fake_mirror_name]
        self.run(delete_mirror_cmd)

        return True


class UpdaterConfiguration():
    def __init__(self, input_file):
        try:
            self.config = self.load_config_file(input_file)

            self.architectures = self.config['architectures']
            self.component = self.config['component']
            self.filter_formula = self.config['filter_formula']
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

    config = UpdaterConfiguration(args.config_file[0])


if __name__ == '__main__':
    main()
