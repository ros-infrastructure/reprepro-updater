#!/bin/bash


reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter oneiric "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu removefilter oneiric "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter oneiric "Package (% ros-unstable*)" | wc -l

reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter natty "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu removefilter natty "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter natty "Package (% ros-unstable*)" | wc -l

reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter maverick "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu removefilter maverick "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter maverick "Package (% ros-unstable*)" | wc -l

reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter lucid "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu removefilter lucid "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter lucid "Package (% ros-unstable*)" | wc -l

reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter karmic "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu removefilter karmic "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter karmic "Package (% ros-unstable*)" | wc -l

reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter jaunty "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu removefilter jaunty "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter jaunty "Package (% ros-unstable*)" | wc -l

reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter hardy "Package (% ros-unstable*)" | wc -l
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu removefilter hardy "Package (% ros-unstable*)" 
reprepro -v -b /var/www/repos/ros-shadow-fixed/ubuntu listfilter hardy "Package (% ros-unstable*)" | wc -l
