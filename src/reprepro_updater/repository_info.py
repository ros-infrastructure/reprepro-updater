import os


class RepositoryInfo:
    """
    Parse apt repository data in order to provide information for reprepro-updater.
    """
    def __init__(self, repo_dir, distro, arch):
        self.repo_dir = repo_dir
        self.distro = distro
        self.arch = arch
        self.package_dependencies = None
        self.package_rdepends = None

    def _parse_packages_file(self):
        """

        Loads the Packages file for the main repository component and parses
        the dependencies into memory.

        Sets the variable package_dependencies which is a dict of package names
        mapping to sets of dependency names.
        """
        if self.package_dependencies is None:
            self.package_dependencies = {}
        packages_filepath = os.path.join(self.repo_dir, 'dists', self.distro,
                                         'main', 'binary-{}'.format(self.arch), 'Packages')
        packages_contents = open(packages_filepath, "r").read()
        for section in packages_contents.split("\n\n"):
            if section is '':
                continue
            name = None
            depends = None
            for line in section.split("\n"):
                if line.startswith("Package: "):
                    name = line.split(": ")[1]
                if line.startswith("Depends: "):
                    depends = line.split(": ")[1]
            if name is None:
                raise RuntimeError(
                    "Repository file '{}' had a section missing 'Package':\n+\n{}\n+".format(
                        packages_filepath, section))
            if depends is None:
                dependency_set = set()
            else:
                dependency_set = set([item.strip().split(' ')[0] for item in depends.split(',')])
            self.package_dependencies[name.strip()] = dependency_set
        return self.package_dependencies

    def get_rdepends(self, package):
        """
        Get the direct reverse dependencies (dependents) of the given package.

        Uses an internal map of memoized return values to cache results.
        Returns a set of package names that depend directly on the given package.
        """
        if self.package_rdepends is None:
            self.package_rdepends = {}
        if self.package_dependencies is None:
            self._parse_packages_file()

        # Early return a memoized result if previously calculated.
        if package in self.package_rdepends:
            return self.package_rdepends[package]

        rdepends = set()
        for p, dependencies in self.package_dependencies.items():
            if package in dependencies:
                rdepends.add(p)
        self.package_rdepends[package] = rdepends

        return self.package_rdepends[package]
