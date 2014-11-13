#!/usr/bin/env python

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

parser.add_option("-c", "--commit", dest="commit", action='store_true', default=False)


(options, args) = parser.parse_args()

if len(args) < 1:
    parser.error("must be at least two argument, the repository to write into and one or more yaml files")

conf_params = conf.load_conf(args[0])

yaml_files = args[1:]

if not conf_params.repo_exists():
    parser.error("Repository must have been initialized already")


updates_generator = conf.UpdatesFile(ALL_DISTROS, ALL_ARCHES)

dist = conf_params.create_distributions_file(updates_generator)

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
        print "Updating for %s %s to update into repo %s" % (distro, arch, conf_params.repository_path)
        run_update(conf_params.repository_path, dist, updates_generator, distro, arch, options.commit)
