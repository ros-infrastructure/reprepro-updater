#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src


set -o errexit

## Import indigo armhf from experimental farm

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros-shadow-fixed/ubuntu -y /home/rosbuild/reprepro_updater/import/repositories.ros.org_indigo_testing.yaml

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -y /home/rosbuild/reprepro_updater/import/repositories.ros.org_indigo_main.yaml

