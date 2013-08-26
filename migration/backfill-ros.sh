#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src
python /home/rosbuild/reprepro_updater/scripts/setup_repo.py /var/www/repos/ros/ubuntu -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -y /home/rosbuild/reprepro_updater/migration/backfill-ros.yaml -c
