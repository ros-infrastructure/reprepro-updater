from reprepro_updater import conf
from reprepro_updater.conf import ALL_ARCHES, ALL_DISTROS
from reprepro_updater.helpers import LockContext

from optparse import OptionParser

import os
import sys
import subprocess
import time
import yaml

parser = OptionParser()

parser.add_option("-c", "--commit", dest="commit", action='store_true', default=False)
parser.add_option('--gpg-key', dest='gpg_key', action='store', default='B01FA116')

(options, args) = parser.parse_args()
if len(args) != 1:
    parser.error("One argument required")

repo_dir = args[0]
conf_dir = os.path.join(args[0], 'conf')

if not os.path.isdir(conf_dir):
    #parser.error("Argument must be an existing reprepro")
    print "Conf dir did not exist, creating"
    os.makedirs(conf_dir)


dist = conf.DistributionsFile(ALL_DISTROS, ALL_ARCHES, options.gpg_key , None)
inc = conf.IncomingFile(ALL_DISTROS)

distributions_filename = os.path.join(conf_dir, 'distributions')
incoming_filename = os.path.join(conf_dir, 'incoming')



export_command = ['reprepro', '-v', '-b', repo_dir, 'export']

lockfile = os.path.join(repo_dir, 'lock')

with LockContext(lockfile) as lock_c:
    print "I have a lock on %s"% lockfile

    # write out distributions file
    print "Creating distributions file %s" % distributions_filename
    with open(distributions_filename, 'w') as fh:
        fh.write(dist.generate_file_contents('n/a', 'n/a'))

    # write out incoming file
    print "Creating incoming file %s" % incoming_filename
    with open(incoming_filename, 'w') as fh:
        fh.write(inc.generate_file_contents())
    inc.create_required_directories(repo_dir)

    if options.commit:
        print "running command", export_command
        subprocess.check_call(export_command)
    else:
        print "Not running command due to no --commit option"
        print"[%s]" % (  export_command)
