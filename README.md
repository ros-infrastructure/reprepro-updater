This is a set of scripts intended to create/update a debian repository.

A lot of things are currently hard-coded inside.
For example, the default (private) signing key signature (-__-)

Refactoring in progress...

== Creating a new apt repository ==
Add the new distribution in `reprepro_updater`: https://github.com/ros-infrastructure/reprepro-updater/commit/04eb17313ed769d8820ae0168a55ecec7b8de65b
Add the new distribution name in buildfarm_deployment_config (example on the public config: https://github.com/ros-infrastructure/buildfarm_deployment_config/commit/10ce9ec1be1f54865554735082ab7ce1d7a57893)
Log in repos.ros.org as the rosbuild user
go to ~/reprepro_updater/scripts and pull the master branch
run the setup_repo.py script: `python /home/rosbuild/reprepro_updater/scripts/setup_repo.py /var/www/repos/ros_bootstrap/ -c`
Done! You can confirm that the repository has been created by opening http://repos.ros.org/repos/ros_bootstrap/dists/ in your browser

== Import packages in the ROS repos ==

=== Packages released with ros_release_python ===
Just run an import_upstream job on the buildfarm to import the packages from the bootstrap repository to the ROS repositories.

=== Third-party packages imported from PPA ===
- Log in the repos.ros.org machine
```
cd ~/reprepro_updater
. setup.sh
```
- Run a dry run of the import script:
```
python scripts/prepare_sync.py /var/www/repos/ros_bootstrap -y <CONFIG_FILE_WITH_IMPORT_RULE> > tmplog
```
- check the content of tmplog to see if all the changes are the ones youe expect.
`cat tmplog | grep -v keep` is useful to make it quieter

- Run the actual command with -c for commit:
```
python scripts/prepare_sync.py /var/www/repos/ros_bootstrap -y <CONFIG_FILE_WITH_IMPORT_RULE> -c
```

- Trigger an import_upstream job on build.ros.org
This will import the packages from the bootstrap repository to the ROS repositories
