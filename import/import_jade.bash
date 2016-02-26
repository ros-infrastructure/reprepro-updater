#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src


set -o errexit

## Import jade from production buildfarm

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros-shadow-fixed/ubuntu -y /home/rosbuild/reprepro_updater/import/repositories.ros.org_jade_testing.yaml --commit

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -y /home/rosbuild/reprepro_updater/import/repositories.ros.org_jade_main.yaml --commit

