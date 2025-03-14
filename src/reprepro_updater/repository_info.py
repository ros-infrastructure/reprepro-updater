import os


class RepositoryInfo:
    """Parse apt repository data in order to provide information for reprepro-updater."""

    def __init__(self, repo_dir, distro, arch):
        self.repo_dir = repo_dir
        self.distro = distro
        self.arch = arch
        self.package_dependencies = None
        self.package_rdepends = {}

    def _parse_packages_file(self):
        """
        Parse main apt Packages file and load dependencies into memory.

        Sets the variable package_dependencies which is a dict of package names
        mapping to sets of dependency names.
        """
        if self.package_dependencies is None:
            self.package_dependencies = {}
        packages_filepath = os.path.join(
            self.repo_dir, 'dists', self.distro,
            'main', 'binary-{}'.format(self.arch), 'Packages')
        with open(packages_filepath, 'r') as packages_file:
            packages_contents = packages_file.read()
        for section in packages_contents.split('\n\n'):
            if section == '':
                continue
            name = None
            depends = set()
            for line in section.split('\n'):
                if line.startswith('Package: '):
                    name = line.split(': ')[1]
                if line.startswith('Depends: '):
                    depends = {pkg.strip().split(' ')[0] for pkg in line.split(': ')[1].split(',')}
                    # Drop packages from the dependency chain that are not named as ros packages.
                    # This matches the behavior of the _get_dependent_packages reprepro filter.
                    depends = [pkg for pkg in depends if pkg.startswith('ros-')]
            if name is None:
                raise RuntimeError(
                    "Repository file '{}' had a section missing 'Package':\n+\n{}\n+".format(
                        packages_filepath, section))
            name = name.strip()
            # Drop packages from the list of packages that are not named as ros packages.
            # This matches the behavior of the _get_dependent_packages reprepro filter.
            if not name.startswith('ros-'):
                continue
            self.package_dependencies[name] = depends
        return self.package_dependencies

    def get_rdepends(self, package):
        """
        Get the direct reverse dependencies (dependents) of the given package.

        Uses an internal map of memoized return values to cache results.
        Returns a set of package names that depend directly on the given package.
        """
        if self.package_dependencies is None:
            self._parse_packages_file()

        # Early return a memoized result if previously calculated.
        if package in self.package_rdepends:
            return self.package_rdepends[package].copy()

        rdepends = set()
        for p, dependencies in self.package_dependencies.items():
            if package in dependencies:
                rdepends.add(p)
        self.package_rdepends[package] = rdepends

        return self.package_rdepends[package].copy()
