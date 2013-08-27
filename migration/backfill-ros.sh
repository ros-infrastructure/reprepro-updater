#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src
python /home/rosbuild/reprepro_updater/scripts/setup_repo.py /var/www/repos/ros/ubuntu -c

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -d precise -r hydro -a amd64 -u file:///var/www/repos/building/ -cn
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -d precise -r hydro -a i386 -u file:///var/www/repos/building/ -cn

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -d quantal -r hydro -a amd64 -u file:///var/www/repos/building/ -cn
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -d quantal -r hydro -a i386 -u file:///var/www/repos/building/ -cn

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -d raring -r hydro -a amd64 -u file:///var/www/repos/building/ -cn
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -d raring -r hydro -a i386 -u file:///var/www/repos/building/ -cn

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -d precise -r groovy -a amd64 -u file:///var/www/repos/building/ -cn
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -d precise -r groovy -a i386 -u file:///var/www/repos/building/ -cn

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -d quantal -r groovy -a amd64 -u file:///var/www/repos/building/ -cn
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -d quantal -r groovy -a i386 -u file:///var/www/repos/building/ -cn

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -d oneiric -r groovy -a amd64 -u file:///var/www/repos/building/ -cn
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -d oneiric -r groovy -a i386 -u file:///var/www/repos/building/ -cn



python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/ros/ubuntu -y /home/rosbuild/reprepro_updater/migration/backfill-ros.yaml -c
