from reprepro_updater import conf
from reprepro_updater.conf import ALL_ARCHES, ALL_DISTROS
from reprepro_updater.helpers import LockContext, run_update

from optparse import OptionParser

import os
import sys
import subprocess
import time
import yaml

usage = "usage: %prog [options] reprepro_repo yaml_config_file[s]..."

parser = OptionParser(usage=usage)

parser.add_option("-r", "--rosdistro", dest="rosdistro")
parser.add_option("-k", "--sign-key", dest="key", default=None)
parser.add_option("-c", "--commit", dest="commit", action='store_true', default=False)


(options, args) = parser.parse_args()

if len(args) < 1:
    parser.error("must be at least two argument, the directory to write into")

repo_dir = args[0]
conf_dir = os.path.join(args[0], 'conf')

yaml_files = args[1:]

if not os.path.isdir(conf_dir):
    parser.error("Argument must be an existing reprepro")


updates_generator = conf.UpdatesFile([options.rosdistro], ALL_DISTROS, ALL_ARCHES)

dist = conf.DistributionsFile(ALL_DISTROS, ALL_ARCHES, options.key , updates_generator)

target_arches = set()
target_distros = set()

# Parse the upstream yaml files for upstream sources
for fname in yaml_files:
    with open(fname) as fh:
        yaml_dict = yaml.load(fh.read())
        if 'name' not in yaml_dict:
            print "error %s does not include a name element" % fname
            continue
        target_arches.update(set(yaml_dict['architectures']))
        target_distros.update(set(yaml_dict['suites']))
        # TODO add more verification
        updates_generator.add_update_element(conf.UpdateElement(**yaml_dict))


for distro in target_distros:
    for arch in target_arches:
        print "Updating for %s %s to update into repo %s" % (distro, arch, repo_dir)
        run_update(repo_dir, dist, updates_generator, 'rosdistro_na', distro, arch, options.commit)
