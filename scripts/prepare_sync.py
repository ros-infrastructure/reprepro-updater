from reprepro_updater import conf

from reprepro_updater.helpers import LockContext

from optparse import OptionParser

import os
import sys
import subprocess
import time
import yaml

def run_cleanup(repo_dir, rosdistro, distro, arch, commit):
    cleanup_command = ['reprepro', '-v', '-b', repo_dir, '-A', arch, 'removefilter', distro, "Package (%% ros-%s-* )"% rosdistro]


    lockfile = os.path.join(repo_dir, 'lock')
    with LockContext(lockfile) as lock_c:

        if commit:
            print "running command", cleanup_command
            subprocess.check_call(cleanup_command)
        else:
            print "Not cleaning up I would have executed"
            print "[%s]" % cleanup_command

def run_update(repo_dir, dist_generator, updates_generator, rosdistro, distro, arch, commit, invalidate=True):





    update_command = ['reprepro', '-v', '-b', repo_dir, '--noskipold', 'update', distro]

    lockfile = os.path.join(repo_dir, 'lock')

    with LockContext(lockfile) as lock_c:
        print "I have a lock on %s"% lockfile

        # write out update file
        print "Creating updates file %s" % update_filename
        with open(update_filename, 'w') as fh:
            fh.write(updates_generator.generate_file_contents(rosdistro, distro, arch))


        # write out distributions file
        print "Creating distributions file %s" % distributions_filename
        with open(distributions_filename, 'w') as fh:
            fh.write(dist_generator.generate_file_contents(rosdistro, arch))

        if commit:
            print "running command", update_command
            subprocess.check_call(update_command)
        else:
            print "Not executing sync I would have executed:"
            print"[%s]" % (  update_command)


ALL_DISTROS = ['hardy', 'jaunty', 'karmic', 'lucid', 'maverick', 'natty', 'oneiric', 'precise', 'quantal', 'raring', 'wheezy']
ALL_ARCHES =  ['amd64', 'i386', 'armel', 'armhf', 'source']

parser = OptionParser()
parser.add_option("-r", "--rosdistro", dest="rosdistro")
parser.add_option("-a", "--arch", dest="arch")
parser.add_option("-d", "--distro", dest="distro", action='append', default=[])
parser.add_option("-u", "--upstream-ros", dest="upstream_ros", default=None)
parser.add_option("-y", "--yaml-upstream", dest="yaml_upstream", default=[], action='append')

parser.add_option("-c", "--commit", dest="commit", action='store_true', default=False)


(options, args) = parser.parse_args()

if not len(args) == 1:
    parser.error("must be just one argument, the directory to write into")

if not options.upstream_ros and not options.yaml_upstream:
    parser.error("upstream_ros or yaml_upstream required")
elif options.upstream_ros and options.yaml_upstream:
    parser.error("upstream_ros or yaml_upstream required, exclusive")

if not options.distro and options.upstream_ros:
    parser.error("distro required  with upstream ros")

if options.upstream_ros and not [d for d in options.distro if d in ALL_DISTROS]:
    parser.error("invalid distros %s, not in %s" % (options.distro, ALL_DISTROS))

if not options.rosdistro and options.upstream_ros:
    parser.error("rosdistro required  with upstream ros")

if not options.arch and options.upstream_ros:
    parser.error("arch required with upstream ros")

if options.upstream_ros and not options.arch in ALL_ARCHES:
    parser.error("invalid arch %s, not in %s" % (options.arch, ALL_ARCHES))

            

repo_dir = args[0]
conf_dir = os.path.join(args[0], 'conf')

if not os.path.isdir(conf_dir):
    parser.error("Argument must be an existing reprepro")


#inc = conf.IncomingFile(['lucid', 'oneiric', 'precise'])
#print inc.generate_file_contents()



updates_generator = conf.UpdatesFile([options.rosdistro], ALL_DISTROS, ALL_ARCHES, 'B01FA116')
update_filename = os.path.join(conf_dir, 'updates')

dist = conf.DistributionsFile(ALL_DISTROS, ALL_ARCHES, 'B01FA116' , updates_generator)
distributions_filename = os.path.join(conf_dir, 'distributions')


target_arches = set()
target_distros = set()



if options.upstream_ros:
    for ubuntu_distro in options.distro:
        
        d = {'name': 'ros-%s-%s-%s' % \
                 (options.rosdistro, ubuntu_distro, options.arch),
             'method': options.upstream_ros,
             #'rosdistro': options.rosdistro,
             'suites': ubuntu_distro,
             'component': 'main',
             'architectures': options.arch,
             'filter_formula': 'Package (%% ros-%s-*)'%options.rosdistro,
             }

        updates_generator.add_update_element(conf.UpdateElement(**d))

elif options.yaml_upstream:

# Parse the upstream yaml files for addtional upstream sources
    for fname in options.yaml_upstream:
        with open(fname) as fh:
            yaml_dict = yaml.load(fh.read())
            if not 'name' in yaml_dict:
                print "error %s does not include a name element" % fname
                continue
            target_arches.update(set(yaml_dict['architectures']))
            target_distros.update(set(yaml_dict['suites']))
            # TODO add more verification
            updates_generator.add_update_element(conf.UpdateElement(**yaml_dict))






if options.upstream_ros:

    # clean up first
    for distro in options.distro:
        run_cleanup(repo_dir, options.rosdistro, distro, options.arch, options.commit)
    for distro in options.distro:
        run_update(repo_dir, dist, updates_generator, options.rosdistro, distro, options.arch, options.commit)

else:
    
    for distro in target_distros:
        for arch in target_arches:
            print "Updating for %s %s to update into repo %s" % (distro, arch, repo_dir)
            run_update(repo_dir, dist, updates_generator, 'rosdistro_na', distro, arch, options.commit)

