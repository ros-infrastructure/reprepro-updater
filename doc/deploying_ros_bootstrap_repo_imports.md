# Deploying ROS bootstrap repository imports.

## Bootstrap repository access

The ROS bootstrap repository is accessible via ssh to staff with public keys configured in [this private repository](https://github.com/osrf/chef-osrf/tree/latest/data_bags/staff_public_keys).
Generally this access is reserved for staff who need to publish infrastructure packages directly to the bootstrap repository.

Verify access using the command `ssh -T apt@repos.ros.org /bin/true`, if the command exits without error then you have access.
Otherwise you will see a "Permission denied" error.

## Importing packages from reprepro-updater configs.

Reprepro-updater configuration files can be used to directly import packages into a ROS build farm instance.
However for changes to the official build farms we prefer to update the bootstrap repository and run the default import from there which helps ensure that the packages in our bootstrap repostiory are available to other community build farms.

## Updating the bootstrap repository from reprepro-updater

Changes to reprepro-updater *configs* should target the `master` branch of reprepro updater.
The `refactor` branch contains the reprepro-updater library sources used by the build farm.

1. Open a pull request on [ros-infrastructure/reprepro-updater](https://github.com/ros-infrastructure/reprepro-updater).
2. Verify that the source package checks pass on the pull request and review the changes.
3. Once approved and ready for import, merge the pull request.
4. Access `apt@repos.ros.org` via ssh, the following console commands will be run on the repos host.
5. Navigate to the `~/reprepro-updater` repository checkout.
```
cd ~/reprepro-updater
```
6. Update the checkout with the latest changes.
```
git pull origin master
```
7. Run the aptly importer script for the changed configurations
```
python3 scripts/aptly/aptly_importer.py config/PATH_TO_CHANGED_CONFIG
```
The aptly importer will create an aptly mirror (intentionally removing any previous one with the same name if it exists, this is fine) and import matched packages into `ros-bootstrap-$distro` aptly repositories for each configured suite.
Note that is does not update the published repositories at this point, but stages these changes for the next created repository snapshots.
If you need to check which packages were imported to the aptly repository, you can use the usual aptly tools against the `ros_bootstrap-$distro` repository (i.e: `aptly repo search ros_boostrap-focal | grep ignition`).

8. Once all configurations have been updated, run the `snapshot-and-publish-all` script.
```
~/bin/snapshot-and-publish-all ros_bootstrap
```
The script will create new aptly snapshot of ALL the repositories controlled by aptly and switch the public package repositories to these new set of snapshots.
At this point, if no error appeared, the public repositories at <http://repos.ros.org/repos/ros_bootstrap> should contain the new packages.

9. Once this process has completed, trigger `import_upstream` jobs on **both** (no matter if the PR is targeted to just one)  [build.ros.org](https://build.ros.org/job/import_upstream) and [build.ros2.org](https://build.ros2.org/job/import_upstream).
Update the build description with a message about the updated packages and a link to the reprepro-updater PR.
10. Update the reprepro-updater PR with a comment containing links to the import_upstream jobs.
