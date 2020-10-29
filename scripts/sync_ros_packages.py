#!/usr/bin/env python
from __future__ import print_function

import datetime
from optparse import OptionParser
import sys

from reprepro_updater import conf
from reprepro_updater import diff_repos
from reprepro_updater.helpers import run_cleanup
from reprepro_updater.helpers import run_update

parser = OptionParser()
parser.add_option("-r", "--rosdistro", dest="rosdistro")
parser.add_option("-a", "--arch", dest="arches", action='append',
                  default=[], help='Override repo configuration arches')
parser.add_option("-d", "--distro", dest="distros", action='append',
                  default=[], help='Override repo configuration distros')
parser.add_option("-u", "--upstream-ros", dest="upstream_ros", default=None,
                  help="The upstream repository url to pull from, if not a"
                  " local reprepro_config ID")
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
target_repo_url = 'file://' + conf_params.repository_path

if not options.upstream_ros:
    parser.error("upstream-ros required")

upstream_conf_params = conf.load_conf(options.upstream_ros)
if upstream_conf_params:
    upstream_repo_url = "file://" + upstream_conf_params.repository_path
else:
    print("upstream_ros is not a reprepro config, assuming raw method: %s" %
          options.upstream_ros)
    upstream_repo_url = options.upstream_ros

invalid_distros = [d for d in options.distros if d not in conf_params.distros]
if invalid_distros:
    parser.error("invalid distros %s, not in repo configuration: %s" %
                 (invalid_distros, conf_params.distros))

if not options.rosdistro:
    parser.error("rosdistro required")

invalid_arches = [a for a in options.arches
                  if a not in conf_params.architectures]
if invalid_arches:
    parser.error("invalid arches %s, not in repo configuration: %s" %
                 (options.arches,
                  conf_params.architectures))

if options.arches:
    arches = options.arches
else:
    arches = conf_params.architectures

if options.distros:
    distros = options.distros
else:
    distros = conf_params.distros


updates_generator = conf.UpdatesFile(conf_params.distros,
                                     conf_params.architectures)

dist = conf_params.create_distributions_file(updates_generator)

for ubuntu_distro in distros:
    for arch in arches:
        d = {'name': 'ros-%s-%s-%s' %
             (options.rosdistro, ubuntu_distro, arch),
             'method': upstream_repo_url,
             'suites': ubuntu_distro,
             'component': 'main',
             'architectures': arch,
             'filter_formula': 'Package (%% ros-%s-*)' % options.rosdistro,
             }

        updates_generator.add_update_element(conf.UpdateElement(**d))

        # The source architecture doesn't provide a Packages file to diff with.
        # But it should still be added to the updates_generator above so the
        # source repository is updated.
        if arch == 'source':
            print("Not computing diff for source architecture.", file=sys.stderr)
            continue

        package_architecture = 'source' if arch == 'source' else 'binary-' + arch
        # Compute the expected diff for this update element.
        target_url = diff_repos.construct_packages_url(
            target_repo_url,
            ubuntu_distro,
            'main',
            package_architecture)
        upstream_url = diff_repos.construct_packages_url(
            upstream_repo_url,
            ubuntu_distro,
            'main',
            package_architecture)
        try:
            pf_old = diff_repos.get_packagefile_from_url(target_url)
        except RuntimeError as ex:
            print("Exception: %s \n NOT Computing diff" % ex, file=sys.stderr)
            continue
        try:
            pf_new = diff_repos.get_packagefile_from_url(upstream_url)
        except RuntimeError as ex:
            print("Exception: %s \n NOT Computing diff" % ex, file=sys.stderr)
            continue
        dtime = datetime.datetime.now()
        dtime = dtime.replace(microsecond=0)
        print("Difference between '%s' and '%s' computed at %s" %
              (target_url, upstream_url, dtime.isoformat('-')))
        announcement = diff_repos.compute_annoucement(options.rosdistro, pf_old, pf_new)
        print('-' * 80)
        print(announcement)
        print('-' * 80)

# clean up first
if not options.no_cleanup:
    for distro in distros:
        for arch in arches:
            run_cleanup(conf_params.repository_path, options.rosdistro, distro,
                        arch, options.commit)
for distro in distros:
    for arch in arches:
        run_update(conf_params.repository_path, dist, updates_generator,
                   distro, arch, options.commit)
