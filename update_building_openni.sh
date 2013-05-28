#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -c
