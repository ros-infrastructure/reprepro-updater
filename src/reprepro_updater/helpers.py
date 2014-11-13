
import os
import subprocess
import fcntl
import time
import sys


class LockContext:
    def __init__(self, lockfilename=None, timeout=3000):
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
                print "could not get lock on %s." % self.lockfilename
                print "Waiting one second (%d of %d)" % (i, self.timeout)
                time.sleep(1)
        if not file_locked:
            raise IOError("Could not lock file %s with %d retries" %
                          (self.lockfilename, self.timeout))

        return self

    def __exit__(self, exception_type, exception_val, trace):
        self.lfh.close()
        return False


def try_run_command(command):

        try:
            print >>sys.stderr, "running command %s" % command
            subprocess.check_call(command)
            return True

        except Exception, ex:
            print "Execution of [%s] Failed:" % command, ex
            return False


def delete_unreferenced(repo_dir, commit):
    command_argument = 'deleteunreferenced' if commit else 'dumpunreferenced'
    cleanup_command = ['reprepro', '-v', '-b', repo_dir, command_argument]
    print >>sys.stderr, "running", cleanup_command
    return try_run_command(cleanup_command)


def run_include_command(repo_dir, distro, changesfile):
    """ Update the repo to add the files in this changes file """
    # Force misc due to dry packages having invalid "unknown" section,
    # the -S misc can be removed when dry is deprecated.
    include_command = ['reprepro', '-v', '-b', repo_dir, '-S', 'misc',
                       'include', distro, changesfile]
    return try_run_command(include_command)


def _run_update_command(repo_dir, distro, commit):
    """ Update the repo to add the files in this changes file """
    command_argument = 'update' if commit else 'dumpupdate'
    update_command = ['reprepro', '-v', '-b', repo_dir,
                      '--noskipold', command_argument, distro]
    return try_run_command(update_command)


def invalidate_dependent(repo_dir, distro, arch, package):
    """ Remove This all dependencies of the package with the same arch.
    This is only valid for binary packages. """

    invalidate_dependent_command = ['reprepro', '-V', '-b', repo_dir,
                                    '-T', 'deb',
                                    'removefilter', distro,
                                    "Package (% ros-* ), " +
                                    "Architecture (== " + arch + " ), " +
                                    "( Depends (% *" + package + "[, ]* ) " +
                                    "| Depends (% *"+package+" ) )"]
    return try_run_command(invalidate_dependent_command)


def invalidate_package(repo_dir, distro, arch, package):
    """Remove this package itself from the repo"""
    debtype = 'deb' if arch != 'source' else 'dsc'
    arch_match = ', Architecture (== ' + arch + ' )' \
                 if arch != 'source' else ''

    invalidate_package_command = ['reprepro', '-b', repo_dir,
                                  '-T', debtype, '-V',
                                  'removefilter', distro,
                                  "Package (== "+package+" )"+arch_match]

    return try_run_command(invalidate_package_command)


def _clear_ros_distro(repo_dir, rosdistro, distro, arch, commit):
    command_argument = 'removefilter' if commit else 'listfilter'
    cleanup_command = ['reprepro', '-v', '-b', repo_dir, '-A', arch,
                       command_argument, distro,
                       "Package (%% ros-%s-* )" % rosdistro]
    return try_run_command(cleanup_command)


def run_cleanup(repo_dir, rosdistro, distro, arch, commit):

    lockfile = os.path.join(repo_dir, 'lock')
    with LockContext(lockfile) as lock_c:

        _clear_ros_distro(repo_dir, rosdistro, distro, arch, commit)
        delete_unreferenced(repo_dir, commit)


def run_update(repo_dir, dist_generator, updates_generator,
               distro, arch, commit):

    lockfile = os.path.join(repo_dir, 'lock')
    conf_dir = os.path.join(repo_dir, 'conf')
    update_filename = os.path.join(conf_dir, 'updates')
    distributions_filename = os.path.join(conf_dir, 'distributions')

    with LockContext(lockfile) as lock_c:
        print "I have a lock on %s" % lockfile

        # write out update file
        print "Creating updates file %s" % update_filename
        with open(update_filename, 'w') as fh:
            fh.write(updates_generator.generate_file_contents(distro, arch))

        # write out distributions file
        print "Creating distributions file %s" % distributions_filename
        with open(distributions_filename, 'w') as fh:
            fh.write(dist_generator.generate_file_contents(arch))

        _run_update_command(repo_dir, distro, commit)
