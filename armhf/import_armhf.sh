#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src


python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros-shadow-fixed/ubuntu/ -r indigo -d trusty -a armhf -u http://packages.namniart.com/repos/ros -c
