import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_rtab_bringup = get_package_share_directory('rtab_bringup')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # File Paths
    nav2_params_file = os.path.join(pkg_rtab_bringup, 'config', 'param_senior_diff.yaml')
    default_map_path = os.path.join(pkg_rtab_bringup, 'config', 'map.yaml')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=default_map_path,
        description='Full path to map yaml file'
    )

    # 1. Base Robot Description & TF Publisher
    publish_bot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rtab_bringup, 'launch', 'publish_bot.launch.py')
        )
    )

    # 2. Bridge Front LiDAR
    ros_gz_front_scan_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_bridge_front_laser',
        arguments=[
            '/scan_front@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ],
        parameters=[{
            'override_frame_id': 'laser_link',
            'use_sim_time': True
        }],
        output='screen'
    )

    # 3. Bridge Rear LiDAR
    ros_gz_rear_scan_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_bridge_rear_laser',
        arguments=[
            '/scan_rear@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ],
        parameters=[{
            'override_frame_id': 'rear_laser_link',
            'use_sim_time': True
        }],
        output='screen'
    )

    # 4. Merge Dual LiDAR Scans into PointCloud
    scan_merger_node = Node(
        package='ros2_laser_scan_merger',
        executable='ros2_laser_scan_merger',
        name='laser_scan_merger',
        parameters=[{
            'use_sim_time': True,
            'scanTopic1': '/scan_front',
            'scanTopic2': '/scan_rear',
            'pointCloudTopic': '/cloud_in',
            'pointCloutFrameId': 'base_footprint',
            'show1': True,
            'show2': True,
            'laser1XOff': 0.1562,
            'laser1YOff': 0.0,
            'laser1ZOff': 0.1184,
            'laser1Alpha': 0.0,
            'laser2XOff': -0.12,
            'laser2YOff': 0.0,
            'laser2ZOff': 0.18,
            'laser2Alpha': 180.0
        }],
        output='screen'
    )

    # 5. Convert Merged PointCloud to 2D /scan for Nav2
    pointcloud_to_laserscan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        parameters=[{
            'use_sim_time': True,
            'target_frame': 'base_footprint',
            'transform_tolerance': 0.01,
            'min_height': -0.1,
            'max_height': 1.0,
            'angle_min': -3.14159,
            'angle_max': 3.14159,
            'angle_increment': 0.0087,
            'scan_time': 0.1,
            'range_min': 0.12,
            'range_max': 12.0,
            'use_inf': True,
            'inf_epsilon': 1.0
        }],
        remappings=[
            ('cloud_in', '/cloud_in'),
            ('scan', '/scan')
        ],
        output='screen'
    )

    # 6. Nav2 Stack
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

    # 7. RViz2 Node
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
        ros_gz_front_scan_bridge,
        ros_gz_rear_scan_bridge,
        scan_merger_node,
        pointcloud_to_laserscan_node,
        nav2_launch,
        rviz_node
    ])
