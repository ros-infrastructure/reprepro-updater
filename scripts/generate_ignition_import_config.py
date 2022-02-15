#!/usr/bin/env python3

import urllib.request
import sys

from dataclasses import dataclass
from typing import List, Union


@dataclass
class Package:
    name: str
    version: str

class PackagesFile:
    def __init__(self, file_contents):
        self.packages = dict()
        current_package = None
        for line in file_contents.splitlines():
            if line.startswith('Version: '):
                assert current_package
                _, version = line.split(': ')
                self.packages[current_package] = Package(current_package, version)
            if line.startswith('Package: '):
                _, current_package = line.split(': ')


@dataclass
class PackageGroup:
    source_package: str
    packages: None|List[str]
    version_spec: str|None

IGNITION_SUITE='fortress'

PACKAGES = [
        PackageGroup((f'ignition-{IGNITION_SUITE}',), version_spec=None),
        PackageGroup(('ignition-cmake2', 'libignition-cmake2', 'libignition-cmake2-dev'), version_spec=None),
        PackageGroup(('ignition-fuel-tools7', 'libignition-fuel-tools7', 'libignition-fuel-tools7-dev'), version_spec=None),
        PackageGroup(('ignition-gazebo6', 'libignition-gazebo6', 'libignition-gazebo6-dev', 'libignition-gazebo6-plugins'), version_spec=None),
        PackageGroup(('ignition-gui6', 'libignition-gui6', 'libignition-gui6-dev'), version_spec=None),
        PackageGroup(('ignition-launch5', 'libignition-launch5', 'libignition-launch5-dev'), version_spec=None),
        PackageGroup(('ignition-math6', 'libignition-math6', 'libignition-math6-dbg', 'libignition-math6-dev', 'libignition-math6-eigen-dev', 'python3-ignition-math6', 'ruby-ignition-math6'), version_spec=None),
        PackageGroup(('ignition-msgs8', 'libignition-msgs8', 'libignition-msgs8-dev', 'libignition-msgs8-dbg'), version_spec=None),
        PackageGroup(('ignition-physics5',  'libignition-physics5', 'libignition-physics5-bullet','libignition-physics5-bullet-dev',
            'libignition-physics5-core-dev', 'libignition-physics5-dartsim', 'libignition-physics5-dartsim-dev',
            'libignition-physics5-dev', 'libignition-heightmap-dev', 'libignition-physics5-mesh-dev', 'libignition-physics5-sdf-dev',
            'libignition-physics5-tpe', 'libignition-physics5-tpe-dev', 'libignition-physics5-tpelib', 'libignition-physics5-tpelib-dev'
            ), version_spec=None),
        PackageGroup(('ignition-rendering6', 'libignition-rendering6', 'libignition-rendering6-core-dev',
            'libignition-rendering6-dev', 'libignition-rendering6-ogre1', 'libignition-rendering6-ogre1-dev',
            'libignition-rendering6-ogre2', 'libignition-rendering6-ogre2-dev'), version_spec=None),
        PackageGroup(('ignition-sensors6', 'libignition-sensors6', 'libignition-sensors6-air-pressure', 'libignition-sensors6-air-pressure-dev',
            'libignition-sensors6-altimeter', 'libignition-sensors6-altimeter-dev', 'libignition-sensors6-camera', 'libignition-sensors6-camera-dev',
            'libignition-sensors6-depth-camera', 'libignition-sensors6-depth-camera-dev' 'libignition-sensors6-dev',
            'libignition-sensors6-force-torque', 'libignition-sensors6-force-torque-dev', 'libignition-gpu-lidar', 'libignition-gpu-lidar-dev',
            'libignition-imu', 'libignition-imu-dev', 'libignition-sensors6-lidar', 'libignition-sensors6-lidar-dev',
            'libignition-sensors6-logical-camera', 'libignition-sensors6-logical-camera-dev',
            'libignition-sensors6-magnetometer', 'libignition-sensors6-magnetometer-dev', 
            'libignition-sensors6-rendering', 'libignition-sensors6-rendering-dev', 
            'libignition-sensors6-rgbd-camera', 'libignition-sensors6-rgbd-camera-dev', 
            'libignition-sensors6-segmentation-camera', 'libignition-sensors6-segmentation-camera-dev', 
            'libignition-sensors6-thermal-camera', 'libignition-sensors6-thermal-camera-dev'
            ), version_spec=None),
        PackageGroup(('ignition-transport11', 'libignition-transport11', 'libignition-transport11-core-dev',
            'libignition-transport11-dbg', 'libignition-transport11-dev',
            'libignition-transport11-log', 'libignition-transport11-log-dev'), version_spec=None),
        PackageGroup(('ogre-2.2', 'libogre-2.2', 'libogre-2.2-dev'), version_spec=None),
        PackageGroup(('sdformat12', 'libsdformat12', 'libsdformat12-dbg', 'libsdformat12-dev', 'sdformat12-doc', 'sdformat12-sdf'), version_spec=None),
        ]

OS = 'ubuntu'
TARGET_REPO = f'http://packages.osrfoundation.org/gazebo/{OS}-stable'
DISTS = ('focal', 'jammy')
DISTRO = DISTS[1]

resp = urllib.request.urlopen(f'{TARGET_REPO}/dists/{DISTRO}/main/binary-amd64/Packages')
packages_file = PackagesFile(resp.read().decode())

for group in PACKAGES:
    expected_group_version = None
    for p in group.packages:
        if p not in packages_file.packages:
            print(f'Binary package {p} not found in {TARGET_REPO}')
            continue
        if not expected_group_version:
            expected_group_version = packages_file.packages[p].version
        elif packages_file.packages[p].version != expected_group_version:
            print(f'{p} in {group.packages[0]} does not match expected version {expected_group_version}', file=sys.stderr)
            exit(2)
        if not expected_group_version:
            import pdb; pdb.set_trace()
    if expected_group_version:
        package_ver, package_inc = expected_group_version.split('-')
        group.version_spec = f'{package_ver}-*'

print(f'name: ignition_{IGNITION_SUITE}_{OS}_{DISTRO}')
print(f'method: {TARGET_REPO}')
print(f'suites: [{DISTRO}]')
print('component: main')
print('architectures: [amd64, i386, armhf, arm64, source]')
print('filter_formula: "\\')
import pdb; pdb.set_trace()
for pgroup in PACKAGES:
    if not pgroup.version_spec:
        continue
    print('((', end='')
    '|\\\n'.join(f'Package (= {pkg})' for pkg in pgroup.packages)
    print(f'), $Version (% {pgroup.version_spec}))')

