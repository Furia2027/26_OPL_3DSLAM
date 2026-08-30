# Human Recognition

A ROS 2 workspace that functions for bot's self autonomous localization, mapping and navigation
Note : Current version is still in progress and pending testing on simulations.

## Documentation

For more information, check the documentation link below:
https://docs.google.com/document/d/1AXH329UweO3HN9avNHV6fKshVtfs3GVqtQvc72vNd1s/edit?usp=sharing

### Dependencies

* Ubuntu Linux 24.04 Nobble
* ROS 2 Jazzy

### Installation for Packages

* Check Documentation

### Executing program

* Remember to source the workspace first
```
source install/setup.bash
```
* Launching gazebo simulation independently
```
ros2 launch rtab_bringup publish_bot.launch.py
```
* Launching SLAM with gazebo simulation and RVIZ2
```
ros2 launch rtab_bringup slam_sim.launch.py
```
* Launching NAV with gazebo simulation and RVIZ2
```
ros2 launch rtab_bringup nav_sim.launch.py
```

## Authors

Furia2027
[@Furia2027](https://discord.com/users/furia_1001)

## Version History

* Jazzy
