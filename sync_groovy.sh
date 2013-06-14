#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src


wget http://packages.ros.org/ros/ubuntu/dists/precise/main/binary-amd64/Packages -O old_packages
wget http://packages.ros.org/ros-shadow-fixed/ubuntu/dists/precise/main/binary-amd64/Packages -O new_packages
python ~/reprepro_updater/scripts/diff_packages.py old_packages new_packages groovy > logs/groovy_sync_`date +%Y-%m-%d-%T`


python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros/ubuntu -r groovy -d oneiric -d precise -d quantal -a i386 -u file:/var/packages/ros-shadow-fixed/ubuntu -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros/ubuntu -r groovy -d oneiric -d precise -d quantal -a amd64 -u file:/var/packages/ros-shadow-fixed/ubuntu -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros/ubuntu -r groovy -d oneiric -d precise -d quantal -a source -u file:/var/packages/ros-shadow-fixed/ubuntu -c
