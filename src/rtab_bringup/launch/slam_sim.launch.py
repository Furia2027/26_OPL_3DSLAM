import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_rtab_bringup = get_package_share_directory('rtab_bringup')
    rtab_param_path = os.path.join(pkg_rtab_bringup, 'config', 'rtab_param.yaml')

    publish_bot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rtab_bringup, 'launch', 'publish_bot.launch.py')
        )
    )

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
            'range_min': 0.35,
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

    icp_odometry_node = Node(
        package='rtabmap_odom',
        executable='icp_odometry',
        name='icp_odometry',
        output='screen',
        parameters=[rtab_param_path],
        remappings=[
            ('scan', '/scan'),
            ('odom', '/icp_odom')
        ]
    )

    rtabmap_node = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        name='rtabmap',
        output='screen',
        arguments=['-d'],
        parameters=[rtab_param_path],
        remappings=[
            ('rgb/image', '/rtab_cam/image'),
            ('depth/image', '/rtab_cam/depth_image'),
            ('rgb/camera_info', '/rtab_cam/camera_info'),
            ('scan', '/scan'),
            ('odom', '/odometry/filtered'),
            ('imu', '/imu')
        ]
    )

    rtabmap_viz_node = Node(
        package='rtabmap_viz',
        executable='rtabmap_viz',
        name='rtabmap_viz',
        output='screen',
        parameters=[rtab_param_path],
        remappings=[
            ('rgb/image', '/rtab_cam/image'),
            ('depth/image', '/rtab_cam/depth_image'),
            ('rgb/camera_info', '/rtab_cam/camera_info'),
            ('scan', '/scan'),
            ('odom', '/odometry/filtered'),  # Use /odometry/filtered if using EKF output
            ('imu', '/imu')
        ]
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        publish_bot_launch,
        ros_gz_front_scan_bridge,
        ros_gz_rear_scan_bridge,
        scan_merger_node,
        pointcloud_to_laserscan_node,
        icp_odometry_node,
        rtabmap_node,
        rtabmap_viz_node,
        rviz_node
    ])
