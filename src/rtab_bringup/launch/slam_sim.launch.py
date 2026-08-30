import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_rtab_bringup = get_package_share_directory('rtab_bringup')
    pkg_slam_toolbox = get_package_share_directory('slam_toolbox')

    # Path to YAML configuration files
    slam_params_file = os.path.join(pkg_rtab_bringup, 'config', 'slam_sim.yaml')
    laser_filter_file = os.path.join(pkg_rtab_bringup, 'config', 'laser_filter.yaml')
    # 1. Base simulation setup
    publish_bot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rtab_bringup, 'launch', 'publish_bot.launch.py')
        )
    )

    # 2. ROS-Gazebo Bridge for 2D Lidar Scan (Remapped to /scan_raw)
    ros_gz_scan_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ],
        remappings=[
            ('/scan', '/scan_raw')
        ],
        parameters=[{
            'override_frame_id': 'laser_link'
        }],
        output='screen'
    )

    # 3. Laser Filter Node (180-degree front constraint)
    laser_filter_node = Node(
        package='laser_filters',
        executable='scan_to_scan_filter_chain',
        name='laser_filter',
        remappings=[
            ('scan', '/scan_raw'),
            ('scan_filtered', '/scan')
        ],
        parameters=[
            laser_filter_file,
            {'use_sim_time': True}
        ],
        output='screen'
    )

    # 4. SLAM Toolbox (Includes automatic lifecycle management & custom params)
    slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_slam_toolbox, 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'slam_params_file': slam_params_file
        }.items()
    )

    # 5. RViz2 Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        publish_bot_launch,
        ros_gz_scan_bridge,
        laser_filter_node,
        slam_toolbox_launch,
        rviz_node
    ])
