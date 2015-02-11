#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src

# export dump of change
python ~/reprepro_updater/scripts/diff_packages.py /var/www/repos/ros/ubuntu/dists/trusty/main/binary-amd64/Packages /var/www/repos/ros-shadow-fixed/ubuntu/dists/trusty/main/binary-amd64/Packages jade --output-dir ~/reprepro_updater/logs

# i386
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -r jade -d trusty -d utopic -d vivid -a i386 -u file:/var/www/repos/ros-shadow-fixed/ubuntu -c
# amd64
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -r jade -d trusty -d utopic -d vivid -a amd64 -u file:/var/www/repos/ros-shadow-fixed/ubuntu -c
# armhf
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -r jade -d trusty -d utopic -d vivid -a armhf -u file:/var/www/repos/ros-shadow-fixed/ubuntu -c
# source
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -r jade -d trusty -d utopic -d vivid -a source -u file:/var/www/repos/ros-shadow-fixed/ubuntu -c

date