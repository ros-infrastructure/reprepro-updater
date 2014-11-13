from reprepro_updater import conf
from reprepro_updater.conf import ALL_ARCHES, ALL_DISTROS
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
parser.add_option("-k", "--sign-key", dest="key", default=None)
parser.add_option("-u", "--upstream-ros", dest="upstream_ros", default=None)
parser.add_option("-n", "--no-cleanup", dest="no_cleanup", default=False, action='store_true')
parser.add_option("-c", "--commit", dest="commit", action='store_true', default=False)


(options, args) = parser.parse_args()

if not len(args) == 1:
    parser.error("must be just one arguments, the directory to write into")

if not options.distro:
    parser.error("distro required")

if not options.upstream_ros:
    parser.error("upstream-ros required")

if not [d for d in options.distro if d in ALL_DISTROS]:
    parser.error("invalid distros %s, not in %s" % (options.distro, ALL_DISTROS))

if not options.rosdistro:
    parser.error("rosdistro required")

if not options.arch:
    parser.error("arch required")

if options.arch not in ALL_ARCHES:
    parser.error("invalid arch %s, not in %s" % (options.arch, ALL_ARCHES))

repo_dir = args[0]
conf_dir = os.path.join(repo_dir, 'conf')

if not os.path.isdir(conf_dir):
    parser.error("Argument must be an existing reprepro")

updates_generator = conf.UpdatesFile([options.rosdistro], ALL_DISTROS, ALL_ARCHES)
update_filename = os.path.join(conf_dir, 'updates')

dist = conf.DistributionsFile(ALL_DISTROS, ALL_ARCHES, options.key , updates_generator)
distributions_filename = os.path.join(conf_dir, 'distributions')


target_arches = set()
target_distros = set()

for ubuntu_distro in options.distro:

    d = {'name': 'ros-%s-%s-%s' % \
         (options.rosdistro, ubuntu_distro, options.arch),
         'method': options.upstream_ros,
         'suites': ubuntu_distro,
         'component': 'main',
         'architectures': options.arch,
         'filter_formula': 'Package (%% ros-%s-*)'%options.rosdistro,
         }

    updates_generator.add_update_element(conf.UpdateElement(**d))



# clean up first
if not options.no_cleanup:
    for distro in options.distro:
        run_cleanup(repo_dir, options.rosdistro, distro, options.arch, options.commit)
for distro in options.distro:
    run_update(repo_dir, dist, updates_generator, distro, options.arch, options.commit)
