from reprepro_updater import conf

from optparse import OptionParser

import os
import subprocess

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

if not options.rosdistro:
    parser.error("rosdistro required")

if not options.arch:
    parser.error("arch required")

repo_dir = args[0]
conf_dir = os.path.join(args[0], conf)

if not os.path.isdir(conf_dir):
    parser.error("Argument must be an existing reprepro")



#inc = conf.IncomingFile(['lucid', 'oneiric', 'precise'])
#print inc.generate_file_contents()


inc = conf.UpdatesFile(['fuerte', 'groovy'], ['lucid', 'oneiric', 'precise'], ['amd64', 'i386', 'armel', 'source'], 'B01FA116', options.upstream )
update_filename = os.path.join(conf_dir, 'updates')
with open(update_filename, 'w') as fh:
    fh.write(inc.generate_file_contents())



dist = conf.DistributionsFile(['hardy', 'jaunty', 'karmic', 'lucid', 'maverick', 'natty', 'oneiric', 'precise', 'quantal'], ['amd64', 'i386', 'armel', 'source'], 'B01FA116' )

distributions_filename = os.path.join(conf_dir, 'distributions')
with open(distributions_filename, 'w') as fh:
    fh.write(dist.generate_file_contents(options.rosdistro, options.distro, options.arch))


cleanup_command = 

command = ['reprepro', '-v', '-b', repo_dir, 'update', distro]

if options.commit:
    
    subprocess.c
