import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, SetRemap

def generate_launch_description():
    pkg_rtab_bringup = get_package_share_directory('rtab_bringup')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # File Paths
    nav2_params_file = os.path.join(pkg_rtab_bringup, 'config', 'param_senior_diff.yaml')
    laser_filter_file = os.path.join(pkg_rtab_bringup, 'config', 'laser_filter.yaml')
    default_map_path = os.path.join(pkg_rtab_bringup, 'config', 'map.yaml')

    # Launch Arguments
    map_arg = DeclareLaunchArgument(
        'map',
        default_value=default_map_path,
        description='Full path to map yaml file'
    )

    # 1. Base Simulation Setup
    publish_bot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rtab_bringup, 'launch', 'publish_bot.launch.py')
        )
    )

    # 2. ROS-Gazebo Bridge (Remapped to /scan_raw)
    ros_gz_scan_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'],
        remappings=[('/scan', '/scan_raw')],
        parameters=[{'override_frame_id': 'laser_link'},
                    {'use_sim_time': True}],
        output='screen'
    )

    # 3. Laser Filter Node
    laser_filter_node = Node(
        package='laser_filters',
        executable='scan_to_scan_filter_chain',
        name='laser_filter',
        remappings=[
            ('scan', '/scan_raw'),
            ('scan_filtered', '/scan')
        ],
        parameters=[laser_filter_file, {'use_sim_time': True}],
        output='screen'
    )

    # 4. Nav2 Stack ( AMCL + Map Server + Nav2 Lifecycle)
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'map': LaunchConfiguration('map'),
            'params_file': nav2_params_file,
            'autostart': 'true',
            'use_docking': 'false'
        }.items()
    )

    # 5. RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        map_arg,
        publish_bot_launch,
        ros_gz_scan_bridge,
        laser_filter_node,
        nav2_launch,
        rviz_node
    ])
