#!/usr/bin/env python

from reprepro_updater import conf
from reprepro_updater.helpers import LockContext, run_cleanup, run_update

from optparse import OptionParser

import os
import sys
import subprocess
import time
import yaml

parser = OptionParser()
parser.add_option("-r", "--rosdistro", dest="rosdistro")
parser.add_option("-a", "--arch", dest="arch")
parser.add_option("-d", "--distro", dest="distro", action='append', default=[])
parser.add_option("-u", "--upstream-ros", dest="upstream_ros", default=None,
                  help="The upstream repository url to pull from")
parser.add_option("-n", "--no-cleanup", dest="no_cleanup",
                  default=False, action='store_true')
parser.add_option("-c", "--commit", dest="commit",
                  action='store_true', default=False)

(options, args) = parser.parse_args()

if not len(args) == 1:
    parser.error("must be just one arguments, the directory to write into")

conf_params = conf.load_conf(args[0])
if not conf_params.repo_exists():
    parser.error("Repository must have been initialized already")

if not options.distro:
    parser.error("distro required")

if not options.upstream_ros:
    parser.error("upstream-ros required")

invalid_distros = [d for d in options.distro if d not in conf_params.distros]
if invalid_distros:
    parser.error("invalid distros %s, not in repo configuration: %s" %
                 (invalid_distros, conf_params.distros))

if not options.rosdistro:
    parser.error("rosdistro required")

if options.arch not in conf_params.architectures:
    parser.error("invalid arch %s, not in repo configuration: %s" %
                 (options.arch,
                  conf_params.architectures))

updates_generator = conf.UpdatesFile(conf_params.distros,
                                     conf_params.architectures)

dist = conf_params.create_distributions_file(updates_generator)

for ubuntu_distro in options.distro:

    d = {'name': 'ros-%s-%s-%s' %
         (options.rosdistro, ubuntu_distro, options.arch),
         'method': options.upstream_ros,
         'suites': ubuntu_distro,
         'component': 'main',
         'architectures': options.arch,
         'filter_formula': 'Package (%% ros-%s-*)' % options.rosdistro,
         }

    updates_generator.add_update_element(conf.UpdateElement(**d))

# clean up first
if not options.no_cleanup:
    for distro in options.distro:
        run_cleanup(conf_params.repository_path, options.rosdistro, distro,
                    options.arch, options.commit)
for distro in options.distro:
    run_update(conf_params.repository_path, dist, updates_generator,
               distro, options.arch, options.commit)
