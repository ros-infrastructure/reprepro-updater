from __future__ import print_function

import fcntl
import os
import subprocess
import sys
import time

from reprepro_updater.repository_info import RepositoryInfo


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
        for i in range(self.timeout):

            try:

                fcntl.lockf(self.lfh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                file_locked = True
                break
            except IOError:
                print("could not get lock on %s." % self.lockfilename)
                print("Waiting one second (%d of %d)" % (i, self.timeout))
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
            print("running command %s" % command, file=sys.stderr)
            subprocess.check_call(command)
            return True

        except Exception as ex:
            print("Execution of [%s] Failed:" % command, ex)
            return False


def delete_unreferenced(repo_dir, commit):
    command_argument = 'deleteunreferenced' if commit else 'dumpunreferenced'
    cleanup_command = ['reprepro', '-v', '-b', repo_dir, command_argument]
    print("running", cleanup_command, file=sys.stderr)
    return try_run_command(cleanup_command)


def run_include_command(repo_dir, distro, changesfile):
    """Update the repo to add the files in this changes file."""
    # Force misc due to dry packages having invalid "unknown" section,
    # the -S misc can be removed when dry is deprecated.
    include_command = ['reprepro', '-v', '-b', repo_dir, '-S', 'misc',
                       'include', distro, changesfile]
    return try_run_command(include_command)


def _run_update_command(repo_dir, distro, commit):
    """Update the repo to add the files in this changes file."""
    command_argument = 'update' if commit else 'dumpupdate'
    update_command = ['reprepro', '-v', '-b', repo_dir,
                      '--noskipold', command_argument, distro]
    return try_run_command(update_command)


def invalidate_packages(repo_dir, distro, arch, packages):
    """
    Remove multiple packages from the repo in one reprepro invocation.

    This is only valid for binary packages.
    """
    # Short circuit if there are no packages to remove.
    if not packages:
        print('No packages to remove. Not invoking reprepro.')
        return True
    filterstr = 'Package (== {})'
    filterlist = [filterstr.format(pkgname) for pkgname in packages]
    cmd_prefix = ['reprepro', '-b', repo_dir, '-T', 'deb',
                  '-A', arch, '-V', 'removefilter', distro]
    invalidate_packages_command = cmd_prefix + [' | '.join(filterlist)]

    # We first attempt to run the full list of packages.  However, this may
    # fail if the package list is too long.  In that case, we split the list
    # in half and try again.
    if not try_run_command(invalidate_packages_command):
        half = len(filterlist) // 2

        invalidate1 = cmd_prefix + [' | '.join(filterlist[:half])]
        invalidate2 = cmd_prefix + [' | '.join(filterlist[half:])]

        ret = try_run_command(invalidate1)
        ret = ret and try_run_command(invalidate2)
    else:
        ret = True

    return ret


def invalidate_package(repo_dir, distro, arch, package):
    """Remove this package itself from the repo."""
    debtype = 'deb' if arch != 'source' else 'dsc'
    arch_match = ', Architecture (== ' + arch + ' )' \
                 if arch != 'source' else ''

    invalidate_package_command = ['reprepro', '-b', repo_dir,
                                  '-T', debtype, '-V',
                                  'removefilter', distro,
                                  'Package (== ' + package + ' )' + arch_match]
    return try_run_command(invalidate_package_command)


def invalidate_dependent(repo_dir, distro, arch, package):
    """
    Remove all dependents of the package with the same arch.

    This is only valid for binary packages and assumes all
    packages are in the `main` component.
    """
    # Use internal repository information parser to get reverse dependents.
    # Using reprepro for each package was resulting in huge runtimes causing timeouts
    # on the buildfarm when invalidating low-level packages.
    repo_info = RepositoryInfo(repo_dir, distro, arch)

    # We'll build this into a list of transitive dependents.
    transitive_dependents = repo_info.get_rdepends(package)
    # queue of dependents to iterate, seeded with the initial rdepends.
    dependents_to_process = list(transitive_dependents)

    while dependents_to_process:
        dep = dependents_to_process.pop()
        depdeps = repo_info.get_rdepends(dep)
        dependents_to_process += (depdeps - transitive_dependents)
        transitive_dependents |= depdeps

    return invalidate_packages(repo_dir, distro, arch, transitive_dependents)


def _clear_ros_distro(repo_dir, rosdistro, distro, arch, commit):
    command_argument = 'removefilter' if commit else 'listfilter'
    cleanup_command = ['reprepro', '-v', '-b', repo_dir, '-A', arch,
                       command_argument, distro,
                       "Package (%% ros-%s-* )" % rosdistro]
    return try_run_command(cleanup_command)


def run_cleanup(repo_dir, rosdistro, distro, arch, commit):

    lockfile = os.path.join(repo_dir, 'lock')
    with LockContext(lockfile) as lock_c:

        if not _clear_ros_distro(repo_dir, rosdistro, distro, arch, commit):
            raise RuntimeError('cleanup command failed')
        if not delete_unreferenced(repo_dir, commit):
            raise RuntimeError('delete_unreferenced command failed')


def run_update(repo_dir, dist_generator, updates_generator,
               distro, arch, commit):

    lockfile = os.path.join(repo_dir, 'lock')
    conf_dir = os.path.join(repo_dir, 'conf')
    update_filename = os.path.join(conf_dir, 'updates')
    distributions_filename = os.path.join(conf_dir, 'distributions')

    with LockContext(lockfile) as lock_c:
        print("I have a lock on %s" % lockfile)

        # write out update file
        print("Creating updates file %s" % update_filename)
        update_contents = updates_generator.generate_file_contents(distro, arch)
        for l in update_contents.splitlines():
            print("  %s" % l)
        with open(update_filename, 'w') as fh:
            fh.write(update_contents)

        # write out distributions file
        print("Creating distributions file %s" % distributions_filename)
        with open(distributions_filename, 'w') as fh:
            fh.write(dist_generator.generate_file_contents(arch))

        if not _run_update_command(repo_dir, distro, commit):
            raise RuntimeError('update command failed')
