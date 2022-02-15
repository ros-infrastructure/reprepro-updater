#!/usr/bin/env python3

import urllib.request
import sys

from dataclasses import dataclass
from typing import List, Union


@dataclass
class Package:
    name: str
    source_package: str
    version: str

class PackagesFile:
    def __init__(self, file_contents):
        self.packages = dict()
        current_package = None
        current_source = None
        current_version = None
        for line in file_contents.splitlines():
            if line.startswith('Source: '):
                current_source = line.split(': ')[1]
            if line.startswith('Version: '):
                current_version = line.split(': ')[1]
            if line.startswith('Package: '):
                if current_package:
                    assert current_version and current_source
                    self.packages[current_package] = Package(current_package, current_source, current_version)
                    current_source = None
                    current_version = None
                current_package = line.split(': ')[1]


@dataclass
class PackageGroup:
    source_package: str
    packages: None|List[str]
    version_spec: str|None

IGNITION_SUITE='fortress'

PACKAGES = [
        PackageGroup(f'ignition-{IGNITION_SUITE}', packages=None, version_spec=None),
        PackageGroup('ignition-cmake2', packages=None, version_spec=None),
        PackageGroup('ignition-fuel-tools7', packages=None, version_spec=None),
        PackageGroup('ignition-gazebo6', packages=None, version_spec=None),
        PackageGroup('ignition-gui6', packages=None, version_spec=None),
        PackageGroup('ignition-launch5', packages=None, version_spec=None),
        PackageGroup('ignition-math6', packages=None, version_spec=None),
        PackageGroup('ignition-msgs8', packages=None, version_spec=None),
        PackageGroup('ignition-physics5', packages=None, version_spec=None),
        PackageGroup('ignition-rendering6', packages=None, version_spec=None),
        PackageGroup('ignition-sensors6', packages=None, version_spec=None),
        PackageGroup('ignition-transport11', packages=None, version_spec=None),
        PackageGroup('ogre-2.2', packages=None, version_spec=None),
        PackageGroup('sdformat12', packages=None, version_spec=None),
    ]

OS = 'debian'
TARGET_REPO = f'http://packages.osrfoundation.org/gazebo/{OS}-stable'
DISTS = ('focal', 'jammy', 'bullseye', 'buster')
DISTRO = DISTS[2]

resp = urllib.request.urlopen(f'{TARGET_REPO}/dists/{DISTRO}/main/binary-amd64/Packages')
packages_file = PackagesFile(resp.read().decode())

for group in PACKAGES:
    expected_group_version = None
    group.packages = [pkg.name for pkg in packages_file.packages.values() if pkg.source_package == group.source_package]
    for p in group.packages:
        if not expected_group_version:
            expected_group_version = packages_file.packages[p].version
        elif packages_file.packages[p].version != expected_group_version:
            print(f'{p} in {group.packages[0]} does not match expected version {expected_group_version}', file=sys.stderr)
            exit(2)
    if expected_group_version:
        package_ver, package_inc = expected_group_version.split('-')
        group.version_spec = f'{package_ver}-*'
    group.packages.insert(0, group.source_package)

print(f'name: ignition_{IGNITION_SUITE}_{OS}_{DISTRO}')
print(f'method: {TARGET_REPO}')
print(f'suites: [{DISTRO}]')
print('component: main')
print('architectures: [amd64, i386, armhf, arm64, source]')
print('filter_formula: "\\')
printable_groups = [pgroup for pgroup in PACKAGES if pgroup.version_spec]
for idx in range(0, len(printable_groups)):
    pgroup = printable_groups[idx]
    if not pgroup.version_spec:
        continue
    print('(', end='')
    print(' |\\\n '.join(f'(Package (= {name})' for name in pgroup.packages))
    print(f'), $Version (% {pgroup.version_spec})', end='')
    if idx != len(printable_groups) - 1:
        print(' |\\')
    else:
        print(' \\\n"')


