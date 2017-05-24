#!/usr/bin/env python

from __future__ import print_function

from optparse import OptionParser

import os
import shutil
import sys

from reprepro_updater.changes_parsing import find_changes_files
from reprepro_updater.changes_parsing import load_changes_files
from reprepro_updater.helpers import delete_unreferenced
from reprepro_updater.helpers import invalidate_dependent
from reprepro_updater.helpers import invalidate_package
from reprepro_updater.helpers import LockContext
from reprepro_updater.helpers import run_include_command

parser = OptionParser()

parser.add_option("--delete-folder", dest="do_delete",
                  action='store_true', default=False)

parser.add_option("-f", "--folder", dest="folders", action="append")
parser.add_option("-p", "--package", dest="package")

parser.add_option("-c", "--commit", dest="commit",
                  action='store_true', default=False)
parser.add_option("--invalidate", dest="invalidate",
                  action='store_true', default=False)

parser.add_option("--repo-path", dest="repo_path",
                  default='/var/repos/ubuntu/building')

(options, args) = parser.parse_args()


for f in options.folders:
    if not os.path.isdir(f):
        parser.error("Folder option must be a folder: %s" % f)

changes_filenames = []
for folder in options.folders:
    changes_filenames.extend(find_changes_files(folder))
changefiles = load_changes_files(changes_filenames)

if not changefiles:
    parser.error("Folders %s doesn't contain a changes file. %s" %
                 (options.folders, [os.listdir(f) for f in options.folders]))

valid_changes = [c for c in changefiles
                 if options.package in c.content['Binary'].split()]

extraneous_packages = set(changefiles) - set(valid_changes)
if extraneous_packages:
    parser.error("Invalid packages detected in folders %s."
                 " Expected [%s], got [%s] from file %s" %
                 (options.folders, options.package,
                  [e.content['Binary'] for e in extraneous_packages],
                  [e.filename for e in extraneous_packages]))

lockfile = os.path.join(options.repo_path, 'lock')

if options.commit:
    with LockContext(lockfile) as lock_c:

        # invalidate and clear all first

        # only invalidate dependencies if invalidation is asked for
        for changes in valid_changes:
            if options.invalidate:
                if changes.content['Architecture'] != 'source':
                    if not invalidate_dependent(options.repo_path,
                                                changes.content['Distribution'],
                                                changes.content['Architecture'],
                                                options.package):
                        sys.exit(1)

            # always invalidate this package we're about to upload the new one
            if not invalidate_package(options.repo_path,
                                      changes.content['Distribution'],
                                      changes.content['Architecture'],
                                      options.package):
                sys.exit(1)

        # delete_unreferenced before uploading if invalidating
        if not delete_unreferenced(options.repo_path, options.commit):
            sys.exit(1)

        # update after clearing all
        for changes in valid_changes:
            package_str_parts = []
            if changes.content['Architecture'] == 'source':
                package_str_parts.append(changes.content['Source'])
            else:
                package_str_parts.append(changes.content['Binary'])
            package_str_parts.append(changes.content['Version'])
            package_str_parts.append(changes.content['Distribution'])
            package_str_parts.append(changes.content['Architecture'])
            print('Importing package: %s' % ':'.join(package_str_parts))

            if not run_include_command(options.repo_path,
                                       changes.content['Distribution'],
                                       changes.filename):
                sys.exit(1)
            if options.do_delete:
                print("Removing %s" % changes.folder)
                shutil.rmtree(changes.folder)

else:
    print("NO COMMIT OPTION\nWould have run invalidation of"
          " dependent packages, invalidation of %s package and "
          "uploaded new package" % (options.package), file=sys.stderr)
