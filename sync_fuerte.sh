#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src

wget http://packages.ros.org/ros/ubuntu/dists/lucid/main/binary-amd64/Packages -O old_packages
wget http://packages.ros.org/ros-shadow-fixed/ubuntu/dists/lucid/main/binary-amd64/Packages -O new_packages
python ~/reprepro_updater/scripts/diff_packages.py old_packages new_packages fuerte > logs/fuerte_sync_`date +%Y-%m-%d-%T`




python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros/ubuntu -r fuerte -d lucid -d oneiric -d precise -a i386 -u file:/var/packages/ros-shadow-fixed/ubuntu -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros/ubuntu -r fuerte -d lucid -d oneiric -d precise -a amd64 -u file:/var/packages/ros-shadow-fixed/ubuntu -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/packages/ros/ubuntu -r fuerte -d lucid -d oneiric -d precise -a source -u file:/var/packages/ros-shadow-fixed/ubuntu -c
