#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/import/import_upstream.yaml -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros-shadow-fixed/ubuntu -y /home/rosbuild/reprepro_updater/import/import_upstream.yaml -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -y /home/rosbuild/reprepro_updater/import/import_upstream.yaml -c



