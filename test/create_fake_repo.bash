#/bin/bash

set -e

REPO_PATH=/tmp/fake_repo
TEST_PKG=http://packages.osrfoundation.org/gazebo/ubuntu-stable/pool/main/s/sdformat9/sdformat9-sdf_9.3.0-1~bionic_all.deb

mkdir -p ${REPO_PATH}/conf
cat > ${REPO_PATH}/conf/distributions <<- EOF
Origin: repo.example.com
Label: repo.example.com
Codename: bionic
Architectures: i386 amd64 source
Components: main
Description: example repo
EOF

wget ${TEST_PKG} -O /tmp/foo.deb
reprepro -b ${REPO_PATH} includedeb bionic /tmp/foo.deb
