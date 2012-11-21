from reprepro_updater import conf

from reprepro_updater.helpers import try_run_command, LockContext

from optparse import OptionParser

import os
import sys
import subprocess
import time

ALL_DISTROS = ['hardy', 'jaunty', 'karmic', 'lucid', 'maverick', 'natty', 'oneiric', 'precise', 'quantal']
ALL_ROSDISTROS = ['electric', 'fuerte', 'groovy']
ALL_ARCHES =  ['amd64', 'i386', 'armel', 'source']

parser = OptionParser()
parser.add_option("-r", "--rosdistro", dest="rosdistro")
parser.add_option("-a", "--arch", dest="arch")
parser.add_option("-d", "--distro", dest="distro")
parser.add_option("-u", "--upstream", dest="upstream", default='http://50.28.27.175/repos/building')

parser.add_option("-c", "--commit", dest="commit", action='store_true', default=False)


(options, args) = parser.parse_args()

if not len(args) == 1:
    parser.error("must be just one argument, the directory to write into")

if not options.distro:
    parser.error("distro required")

if not options.distro in ALL_DISTROS:
    parser.error("invalid distro %s, not in %s" % (options.distro, ALL_DISTROS))

if not options.rosdistro:
    parser.error("rosdistro required")

if not options.arch:
    parser.error("arch required")

if not options.arch in ALL_ARCHES:
    parser.error("invalid arch %s, not in %s" % (options.arch, ALL_ARCHES))


repo_dir = args[0]
conf_dir = os.path.join(args[0], 'conf')

if not os.path.isdir(conf_dir):
    parser.error("Argument must be an existing reprepro")



#inc = conf.IncomingFile(['lucid', 'oneiric', 'precise'])
#print inc.generate_file_contents()


method = options.upstream if options.rosdistro != 'electric' else 'file:/var/packages/ros-shadow/ubuntu'

updates_generator = conf.UpdatesFile([options.rosdistro], ALL_DISTROS, ALL_ARCHES, 'B01FA116', method )
update_filename = os.path.join(conf_dir, 'updates')




dist = conf.DistributionsFile(ALL_DISTROS, ALL_ARCHES, 'B01FA116' )

distributions_filename = os.path.join(conf_dir, 'distributions')



cleanup_command = ['reprepro', '-v', '-b', repo_dir, '-A', options.arch, 'removefilter', options.distro, "Package (%% ros-%s-* )"% options.rosdistro]

update_command = ['reprepro', '-v', '-b', repo_dir, 'update', options.distro]

        


lockfile = os.path.join(repo_dir, 'lock')

with LockContext(lockfile) as lock_c:
    print "I have a lock"

    # write out update file
    with open(update_filename, 'w') as fh:
        fh.write(updates_generator.generate_file_contents())

    # write out distributions file
    with open(distributions_filename, 'w') as fh:
        fh.write(dist.generate_file_contents(options.rosdistro, options.distro, options.arch))

    if options.commit:
        print "running command", cleanup_command
        subprocess.check_call(cleanup_command)
        print "running command", update_command
        subprocess.check_call(update_command)



    
