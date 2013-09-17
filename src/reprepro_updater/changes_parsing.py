import os
import yaml


class ChangesFile:
    def __init__(self, filename):
        try:
            self.filename = filename
            self.yaml_content = yaml.load(open(filename).read())
            self.architecture = self.yaml_content['Architecture']
            self.distro = self.yaml_content['Distribution']
            self.package = self.yaml_content['Binary']
            self.folder = os.path.dirname(filename)
        except Exception, ex:
            raise Exception("Failed to load changes file %s.  [[%s]]" %
                            (filename, ex))


def find_changes_files(folder):
    changesfiles = []
    for f in os.listdir(folder):
        if f.endswith('.changes'):
            changesfiles.append(os.path.join(folder, f))
    return changesfiles


def load_changes_files(changes_files):
    changesfile_objs = []
    for f in changes_files:
        changesfile_objs.append(ChangesFile(f))
    return changesfile_objs
