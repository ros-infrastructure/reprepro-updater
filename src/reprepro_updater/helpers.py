

import subprocess
import fcntl
import time
import sys


class LockContext:
    def __init__(self, lockfilename = None, timeout = 3000):
        if lockfilename:
            self.lockfilename = lockfilename
        else:
            self.lockfilename = '/tmp/prepare_sync.py.lock'

        self.timeout = timeout

    def __enter__(self):
        self.lfh = open(self.lockfilename, 'w')

        file_locked = False
        for i in xrange(self.timeout):

            try:

                fcntl.lockf(self.lfh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                file_locked = True
                break
            except IOError, ex:
                print "could not get lock on %s. Waiting one second (%d of %d)" % (self.lockfilename, i, self.timeout)
                time.sleep(1)
        if not file_locked:
            raise IOError("Could not lock file %s with %d retries"% (self.lockfilename, self.timeout) )

        return self

    def __exit__(self, exception_type, exception_val, trace):
        self.lfh.close()
        return False


def try_run_command(command):

        try:
            subprocess.check_call(command)
            return True

        except Exception, ex:
            print "Execution of [%s] Failed:" % command, ex
            return False


def delete_unreferenced(repo_dir):
    cleanup_command = ['reprepro', '-v', '-b', repo_dir, 'deleteunreferenced']
    print >>sys.stderr, "running", cleanup_command
    return try_run_command(cleanup_command)


def run_update_command(repo_path, distro, changesfile):
    """ Update the repo to add the files in this changes file """
    # Force misc due to dry packages having invalid "unknown" section, the -S misc can be removed when dry is deprecated. 
    update_command = ['reprepro', '-v', '-b', repo_path, '-S', 'misc', 'include', distro, changesfile]
    print >>sys.stderr, "running command %s" % update_command
    return try_run_command(update_command)


def invalidate_dependent(repo_path, distro, arch, package):
    """ Remove This all dependencies of the package with the same arch. 
    This is only valid for binary packages. """

    invalidate_dependent_command = ['reprepro', '-V', '-b', repo_path,
                                    '-T', 'deb',
                                    'removefilter', distro,
                                    "Package (% ros-* ), " +
                                    "Architecture (== " + arch + " ), " +
                                    "( Depends (% *" + package + "[, ]* ) " +
                                    "| Depends (% *"+package+" ) )"]

    print >>sys.stderr, "running", invalidate_dependent_command
    return try_run_command(invalidate_dependent_command)


def invalidate_package(repo_path, distro, arch, package):
    """Remove this package itself from the repo"""
    debtype = 'deb' if arch != 'source' else 'dsc'
    arch_match = ', Architecture (== ' + arch + ' )' if arch != 'source' else ''

    invalidate_package_command = ['reprepro', '-b', repo_path,
                                  '-T', debtype, '-V',
                                  'removefilter', distro,
                                  "Package (== "+package+" )"+arch_match]

    print >>sys.stderr, "running", invalidate_package_command
    return try_run_command(invalidate_package_command)
