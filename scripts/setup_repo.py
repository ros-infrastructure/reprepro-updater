#!/usr/bin/env python

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

parser.add_option("-c", "--commit", dest="commit",
                  action='store_true', default=False)


(options, args) = parser.parse_args()
if len(args) != 1:
    parser.error("One argument required")


conf_params = conf.load_conf(args[0])

conf_dir = os.path.join(conf_params.repository_path, 'conf')

if not os.path.isdir(conf_dir):
    print "Conf dir did not exist, creating %s" % conf_params.repository_path
    os.makedirs(conf_dir)


dist = conf_params.create_distributions_file(None)
inc = conf.IncomingFile(ALL_DISTROS)

export_command = ['reprepro', '-v', '-b',
                  conf_params.repository_path, 'export']

with LockContext(conf_params.lockfile) as lock_c:
    print "I have a lock on %s" % conf_params.lockfile

    # write out distributions file
    distributions_filename = conf_params.distributions_filename()
    print "Creating distributions file %s" % distributions_filename
    with open(distributions_filename, 'w') as fh:
        fh.write(dist.generate_file_contents('n/a'))

    # write out incoming file
    incoming_filename = conf_params.incoming_filename()
    print "Creating incoming file %s" % incoming_filename
    with open(incoming_filename, 'w') as fh:
        fh.write(inc.generate_file_contents())
    inc.create_required_directories(conf_params.repository_path)

    if options.commit:
        print "running command", export_command
        subprocess.check_call(export_command)
    else:
        print "Not running command due to no --commit option"
        print"[%s]" % (export_command)
