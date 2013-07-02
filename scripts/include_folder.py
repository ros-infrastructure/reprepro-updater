from optparse import OptionParser

import os
import sys
import shutil 

from reprepro_updater.helpers import try_run_command, LockContext, delete_unreferenced

ALL_DISTROS = ['hardy', 'jaunty', 'karmic', 'lucid', 'maverick', 'natty', 'oneiric', 'precise', 'quantal', 'raring', 'wheezy']

ALL_ARCHES =  ['amd64', 'i386', 'armel', 'armhf', 'source']

parser = OptionParser()

parser.add_option("--delete-folder", dest="do_delete", action='store_true', default=False)

parser.add_option("-d", "--distro", dest="distro")
parser.add_option("-a", "--arch", dest="arch")

parser.add_option("-f", "--folder", dest="folder")
parser.add_option("-p", "--package", dest="package")

parser.add_option("-c", "--commit", dest="commit", action='store_true', default=False)
parser.add_option("--invalidate", dest="invalidate", action='store_true', default=False)

parser.add_option("--repo-path", dest="repo_path", default='/var/www/repos/building')


(options, args) = parser.parse_args()

if not options.distro:
    parser.error("distro required")

if not options.distro in ALL_DISTROS:
    parser.error("invalid distro %s, not in %s" % (options.distro, ALL_DISTROS))

if not options.arch:
    parser.error("arch required")

if not options.arch in ALL_ARCHES:
    parser.error("invalid arch %s, not in %s" % (options.arch, ALL_ARCHES))


if not os.path.isdir(options.folder):
    parser.error("Folder option must be a folder: %s" % options.folder)

    #cleanup_command = ['reprepro', '-v', '-b', options.repo_path, '-A', options.arch, 'removefilter', options.distro, "Package (%% ros-%s-* )"% options.rosdistro]

changesfile = None

for f in os.listdir(options.folder):
    if f.endswith('.changes'):
        changesfile = os.path.join(options.folder, f)
        break

if not changesfile:
    parser.error("Folder %s doesn't contain a changes file. %s" % (options.folder, os.listdir(options.folder)))

# Force misc due to dry packages having invalid "unknown" section, the -S misc can be removed when dry is deprecated. 
update_command = ['reprepro', '-v', '-b', options.repo_path, '-S', 'misc', 'include', options.distro, changesfile]


debtype = 'deb' if options.arch != 'source' else 'dsc'
arch_match = ', Architecture (== ' + options.arch + ' )' if options.arch != 'source' else ''

invalidate_dependent_command = ['reprepro', '-b', options.repo_path, '-T', debtype, '-V', 'removefilter', options.distro,
                              "Package (% ros-* )"+arch_match+", ( Depends (% *"+options.package+"[, ]* ) | Depends (% *"+options.package+" ) )"]

invalidate_package_command = ['reprepro', '-b', options.repo_path, '-T', debtype, '-V', 'removefilter', options.distro,
                              "Package (== "+options.package+" )"+arch_match]



lockfile = os.path.join(options.repo_path, 'lock')



if options.commit:
    with LockContext(lockfile) as lock_c:

        if options.invalidate:
            if options.arch != 'source':
                print >>sys.stderr, "running", invalidate_dependent_command
                if not try_run_command(invalidate_dependent_command):
                    sys.exit(1)

            print >>sys.stderr, "running", invalidate_package_command
            if not try_run_command(invalidate_package_command):
                sys.exit(1)
                
            if not delete_unreferenced(options.repo_path):
                sys.exit(1)


        print >>sys.stderr, "running command %s" % update_command

        if not try_run_command(update_command):
            sys.exit(1)
        if options.do_delete:
            print "Removing %s" % options.folder
            shutil.rmtree(options.folder)

else:
    print >>sys.stderr, "NO COMMIT OPTION\nWould have run: ", invalidate_dependent_command, "\nThen ", invalidate_package_command, "\nThen ", update_command
