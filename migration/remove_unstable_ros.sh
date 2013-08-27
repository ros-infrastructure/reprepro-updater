#!/bin/bash


reprepro -v -b /var/www/repos/ros/ubuntu listfilter oneiric "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros/ubuntu removefilter oneiric "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros/ubuntu listfilter oneiric "Package (% ros-unstable*)" | wc -l

reprepro -v -b /var/www/repos/ros/ubuntu listfilter natty "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros/ubuntu removefilter natty "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros/ubuntu listfilter natty "Package (% ros-unstable*)" | wc -l

reprepro -v -b /var/www/repos/ros/ubuntu listfilter maverick "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros/ubuntu removefilter maverick "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros/ubuntu listfilter maverick "Package (% ros-unstable*)" | wc -l

reprepro -v -b /var/www/repos/ros/ubuntu listfilter lucid "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros/ubuntu removefilter lucid "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros/ubuntu listfilter lucid "Package (% ros-unstable*)" | wc -l

reprepro -v -b /var/www/repos/ros/ubuntu listfilter karmic "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros/ubuntu removefilter karmic "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros/ubuntu listfilter karmic "Package (% ros-unstable*)" | wc -l

reprepro -v -b /var/www/repos/ros/ubuntu listfilter jaunty "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros/ubuntu removefilter jaunty "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros/ubuntu listfilter jaunty "Package (% ros-unstable*)" | wc -l

reprepro -v -b /var/www/repos/ros/ubuntu listfilter hardy "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros/ubuntu removefilter hardy "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros/ubuntu listfilter hardy "Package (% ros-unstable*)" | wc -l
