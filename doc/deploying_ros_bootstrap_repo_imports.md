# Deploying ROS bootstrap repository imports.

## Bootstrap repository access

The ROS bootstrap repository is accessible via ssh to staff with public keys configured in [this private repository](https://github.com/osrf/chef-osrf/tree/latest/data_bags/staff_public_keys).
Generally this access is reserved for staff who need to publish infrastructure packages directly to the bootstrap repository.

Verify access using the command `ssh -T repos.ros.org /bin/true`, if the command exits without error then you have access.
Otherwise you will see a "Permission denied" error.

## Importing packages from reprepro-updater configs.

Reprepro-updater configuration files can be used to directly import packages into a ROS build farm instance.
However for changes to the official build farms we prefer to update the bootstrap repository and run the default import from there which helps ensure that the packages in our bootstrap repostiory are available to other community build farms.

## Updating the bootstrap repository from reprepro-updater

Changes to reprepro-updater *configs* should target the `master` branch of reprepro updater.
The `refactor` branch contains the reprepro-updater library sources used by the build farm.

1. Open a pull request on [ros-infrastructure/reprepro-updater](https://github.com/ros-infrastructure/reprepro-updater).
1. Verify that the source package checks pass on the pull request and review the changes.
1. Once approved and ready for import, merge the pull request.
1. Access repos.ros.org via ssh, the following console commands will be run on the repos host.
1. Navigate to the `~/reprepro-updater` repository checkout.
```
cd ~/reprepro-updater
```
1. Update the checkout with the latest changes.
```
git pull origin master
```
1. Run the aptly importer script for the changed configurations
```
python3 scripts/aptly/aptly_importer.py config/PATH_TO_CHANGED_CONFIG
```
1. Once all configurations have been updated, run the `snapshot-and-publish-all` script.
```
~/bin/snapshot-and-publish-all ros_bootstrap
```
1. Once this process has completed, trigger `import_upstream` jobs on both build.ros.org and build.ros2.org
Update the build description with a message about the updated packages and a link to the reprepro-updater PR.
1. Update the reprepro-updater PR with a comment containing links to the import_upstream jobs.
