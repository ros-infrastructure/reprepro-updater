from reprepro_updater import conf

from reprepro_updater.helpers import LockContext

from optparse import OptionParser

import os
import sys
import subprocess
import time
import yaml

ALL_DISTROS = ['hardy', 'jaunty', 'karmic', 'lucid', 'maverick', 'natty', 'oneiric', 'precise', 'quantal', 'raring', 'wheezy']
ALL_ARCHES =  ['amd64', 'i386', 'armel', 'armhf', 'source']

parser = OptionParser()
parser.add_option("-r", "--rosdistro", dest="rosdistro")
parser.add_option("-a", "--arch", dest="arch")
parser.add_option("-d", "--distro", dest="distro")
parser.add_option("-u", "--upstream", dest="upstream", default=None)
parser.add_option("-y", "--yaml-upstream", dest="yaml_upstream", default=[], action='append')

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



updates_generator = conf.UpdatesFile([options.rosdistro], ALL_DISTROS, ALL_ARCHES, 'B01FA116', options.upstream )
update_filename = os.path.join(conf_dir, 'updates')

# Parse the upstream yaml files for addtional upstream sources
if options.yaml_upstream:
    for fname in options.yaml_upstream:
        with open(fname) as fh:
            yaml_dict = yaml.load(fh.read())
            if not 'name' in yaml_dict:
                print "error %s does not include a name element" % fname
                continue
            # TODO add more verification
            updates_generator.add_update_element(conf.UpdateElement(**yaml_dict))


dist = conf.DistributionsFile(ALL_DISTROS, ALL_ARCHES, 'B01FA116' , updates_generator)

distributions_filename = os.path.join(conf_dir, 'distributions')



cleanup_command = ['reprepro', '-v', '-b', repo_dir, '-A', options.arch, 'removefilter', options.distro, "Package (%% ros-%s-* )"% options.rosdistro]

update_command = ['reprepro', '-v', '-b', repo_dir, '--noskipold', 'update', options.distro]

        


lockfile = os.path.join(repo_dir, 'lock')

with LockContext(lockfile) as lock_c:
    print "I have a lock on %s"% lockfile

    # write out update file
    print "Creating updates file %s" % update_filename
    with open(update_filename, 'w') as fh:
        fh.write(updates_generator.generate_file_contents(options.rosdistro, options.distro, options.arch))


    # write out distributions file
    print "Creating distributions file %s" % distributions_filename
    with open(distributions_filename, 'w') as fh:
        fh.write(dist.generate_file_contents(options.rosdistro, options.arch))

    if options.commit:
        if options.upstream:
            print "running command", cleanup_command
            subprocess.check_call(cleanup_command)
        else:
            print "Skipping removal of ros packages as upstream not declared"

        print "running command", update_command
        subprocess.check_call(update_command)
    else:
        print "Not executing sync I would have executed:"
        if options.upstream:
            print "[%s]" % cleanup_command
        print"[%s]" % (  update_command)
