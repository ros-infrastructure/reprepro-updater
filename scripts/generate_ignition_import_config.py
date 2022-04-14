#!/usr/bin/env python3

import argparse
import re
import sys
import urllib.request

from dataclasses import dataclass, field
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
                    # Packages without a Source have source name = package name.
                    if current_source is None:
                        current_source = current_package
                    assert current_version
                    self.packages[current_package] = Package(current_package, current_source, current_version)
                    current_source = None
                    current_version = None
                current_package = line.split(': ')[1]
        if current_package not in self.packages:
            self.packages[current_package] = Package(current_package, current_source, current_version)


@dataclass
class PackageGroup:
    source_package: str
    packages: None|List[str]
    version_spec: str|None
    skip_packages: List[str] = field(default_factory=list)

parser = argparse.ArgumentParser(description='Generate import configurations for ignition packages.')
parser.add_argument('--os', type=str)
parser.add_argument('--suite', type=str)
parser.add_argument('--ignition-suite', type=str)
args = parser.parse_args(sys.argv[1:])

package_groups = [
        PackageGroup(f'ignition-{args.ignition_suite}', packages=None, version_spec=None),
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

target_repo = f'http://packages.osrfoundation.org/gazebo/{args.os}-stable'

resp = urllib.request.urlopen(f'{target_repo}/dists/{args.suite}/main/binary-amd64/Packages')
packages_file = PackagesFile(resp.read().decode())

version_spec_re = re.compile('(?P<version>[^-]+)-(?P<inc>\d+)(?P<rest>.*)')
for group in package_groups:
    expected_group_version = None
    group.packages = [pkg.name for pkg in packages_file.packages.values() if pkg.source_package == group.source_package and pkg.name not in group.skip_packages]
    for p in group.packages:
        if not expected_group_version:
            expected_group_version = packages_file.packages[p].version
        elif packages_file.packages[p].version != expected_group_version:
            print(f'{p} in {group.packages[0]} does not match expected version {expected_group_version}', file=sys.stderr)
            exit(2)
    if expected_group_version:
        m = version_spec_re.match(expected_group_version)
        version = m.group('version')
        inc = m.group('inc')
        group.version_spec = f'{version}-{inc}*'
    if group.source_package not in group.packages:
        group.packages.insert(0, group.source_package)

print(f'name: ignition_{args.ignition_suite}_{args.os}_{args.suite}')
print(f'method: {target_repo}')
print(f'suites: [{args.suite}]')
print('component: main')
print('architectures: [amd64, armhf, arm64, source]')
print('filter_formula: "\\')
printable_groups = [pgroup for pgroup in package_groups if pgroup.version_spec]
for idx in range(0, len(printable_groups)):
    pgroup = printable_groups[idx]
    if not pgroup.version_spec:
        continue
    print('(', end='')
    print(' |\\\n '.join(f'Package (= {name})' for name in pgroup.packages), end=' \\\n')
    print(f'), $Version (% {pgroup.version_spec})', end='')
    if idx != len(printable_groups) - 1:
        print(' |\\')
    else:
        print(' \\\n"')
