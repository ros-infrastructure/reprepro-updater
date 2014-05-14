#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src

# export dump of change
python ~/reprepro_updater/scripts/diff_packages.py /var/www/repos/ros/ubuntu/dists/saucy/main/binary-amd64/Packages /var/www/repos/ros-shadow-fixed/ubuntu/dists/saucy/main/binary-amd64/Packages indigo --output-dir ~/reprepro_updater/logs

# i386
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -r indigo -d saucy -d trusty -a i386 -u file:/var/www/repos/ros-shadow-fixed/ubuntu -c
# amd64
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -r indigo -d saucy -d trusty -a amd64 -u file:/var/www/repos/ros-shadow-fixed/ubuntu -c
# source
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -r indigo -d saucy -d trusty -a source -u file:/var/www/repos/ros-shadow-fixed/ubuntu -c
