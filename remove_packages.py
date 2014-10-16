#!/usr/bin/env python

# This is a script to remove packages from all repos quickly.  It will prompt to show what would happen (using listfilter) and the remove using removefilter. 

from __future__ import print_function
import argparse
import subprocess
import sys
import time

DISTROS = ['precise', 'quantal', 'raring', 'saucy', 'trusty']
REPOS = ['/var/www/repos/building', '/var/www/repos/ros-shadow-fixed/ubuntu', '/var/www/repos/ros/ubuntu',]

import argparse

parser = argparse.ArgumentParser(description='Find and remove packages from ROS repos.')
parser.add_argument('regex',
                   help='the regex to use in reprepro')
parser.add_argument('--repo', dest='repos', action='append', default=[],
                    help="Repos to operate on. Default: %s" % REPOS)
parser.add_argument('--distro', dest='distros', action='append', default=[],
                    help="Distros to operate on. Default: %s" % DISTROS)
parser.add_argument('--add', dest='add', action='store_true', default=False,
                    help="Add the filename defined as positional argument.")
parser.add_argument('-n', dest='dry_run', action='store_true', default=False,
                    help="Dry run do not execute, only echo the commands.")
args = parser.parse_args()

if not args.repos:
    args.repos = REPOS

if not args.distros:
    args.distros = DISTROS

def apply_command_template(repo, command_arg, distro, regex, dry_run=False):
    command_template = '/usr/bin/reprepro -b %(repo)s -V %(command_arg)s %(distro)s' % locals()
    if dry_run:
        command_template = 'echo ' + command_template
    _cmd = command_template.split() + [regex]
    print("Running %s" % _cmd)
    subprocess.Popen(_cmd)
    # sleep to let the lock file cleanup before iterating
    print('Sleeping to allow lock reset')
    time.sleep(2.0)
    



for repo in args.repos:
    for distro in args.distros:
        if args.add:
            apply_command_template(repo, 'includedeb', distro, args.regex, args.dry_run)
        else:
            apply_command_template(repo, 'listfilter', distro, args.regex, args.dry_run)


if args.add:
    # short circuit, add was already done
    sys.exit(0)

confirmation = raw_input('Would you like to remove these packages? If so type "yes":')

if confirmation != "yes":
    print('You did not enter "yes" exiting.')
    sys.exit(1)

for repo in args.repos:
    for distro in args.distros:
        apply_command_template(repo, 'removefilter', distro, args.regex, args.dry_run)
