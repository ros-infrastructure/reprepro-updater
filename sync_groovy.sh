#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros/ubuntu -r groovy -d lucid -a i386 -u file:/var/packages/ros-shadow-fixed/ubuntu -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros/ubuntu -r groovy -d lucid -a amd64 -u file:/var/packages/ros-shadow-fixed/ubuntu -c

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros/ubuntu -r groovy -d oneiric -a i386 -u file:/var/packages/ros-shadow-fixed/ubuntu -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros/ubuntu -r groovy -d oneiric -a amd64 -u file:/var/packages/ros-shadow-fixed/ubuntu -c

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros/ubuntu -r groovy -d precise -a i386 -u file:/var/packages/ros-shadow-fixed/ubuntu -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros/ubuntu -r groovy -d precise -a amd64 -u file:/var/packages/ros-shadow-fixed/ubuntu -c
