#!/bin/bash

export PYTHONPATH=/home/rosbuild/reprepro_updater/src

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d lucid -a i386  -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d lucid -a amd64  -c

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d maverick -a i386  -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d maverick -a amd64  -c

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d natty -a i386  -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d natty -a amd64  -c

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d oneiric -a i386  -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d oneiric -a amd64  -c

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d precise -a i386  -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d precise -a amd64  -c

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d quantal -a i386  -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d quantal -a amd64  -c

python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d raring -a i386  -c
python /home/rosbuild/reprepro_updater/scripts/prepare_sync.py /var/www/repos/building -y /home/rosbuild/reprepro_updater/config/openni.upstream.yaml -r electric -d raring -a amd64  -c
