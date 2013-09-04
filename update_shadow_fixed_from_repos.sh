#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src


python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros-shadow-fixed/ubuntu -r hydro -d precise -d quantal -d raring -a i386 -u http://repos.ros.org/repos/ros-shadow-fixed/ubuntu -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros-shadow-fixed/ubuntu -r hydro -d precise -d quantal -d raring -a amd64 -u http://repos.ros.org/repos/ros-shadow-fixed/ubuntu -c 
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros-shadow-fixed/ubuntu -r hydro -d precise -d quantal -d raring -a source -u http://repos.ros.org/repos/ros-shadow-fixed/ubuntu -c
