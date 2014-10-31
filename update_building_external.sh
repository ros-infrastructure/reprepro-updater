#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src

python /home/rosbuild/reprepro_updater/scripts/import_upstream.py /var/www/repos/building /home/rosbuild/reprepro_updater/config/pcl.upstream.yaml  /home/rosbuild/reprepro_updater/config/colladadom.upstream.yaml  /home/rosbuild/reprepro_updater/config/bullet.upstream.yaml  /home/rosbuild/reprepro_updater/config/gazebo.upstream.yaml  /home/rosbuild/reprepro_updater/config/gazebo2.upstream.yaml  /home/rosbuild/reprepro_updater/config/qtsixa.upstream.yaml /home/rosbuild/reprepro_updater/config/catkin_lint.upstream.yaml /home/rosbuild/reprepro_updater/config/ceres.upstream.yaml /home/rosbuild/reprepro_updater/config/urdfdom.upstream.yaml -c
