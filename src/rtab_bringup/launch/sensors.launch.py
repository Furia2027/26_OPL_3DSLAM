import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    realsense_pkg = get_package_share_directory('realsense2_camera')
    ldlidar_pkg = get_package_share_directory('ldlidar_node')

    # RealSense D455 Launch
    realsense_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(realsense_pkg, 'launch', 'rs_launch.py')
        ),
        launch_arguments={
            'align_depth.enable': 'true',
            'enable_sync': 'true',
            'initial_reset': 'false',
            'rgb_camera.profile': '640x480x30',
            'depth_module.profile': '640x480x30',
        }.items()
    )

    # LD06 LiDAR Launch
    ldlidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ldlidar_pkg, 'launch', 'ldlidar_with_mgr.launch.py')
        )
    )

    # TF: base_link -> ldlidar_base
    tf_lidar = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['--x', '0.10', '--y', '0.0', '--z', '0.15',
                   '--yaw', '0', '--pitch', '0', '--roll', '0',
                   '--frame-id', 'base_link', '--child-frame-id', 'ldlidar_base']
    )

    # TF: base_link -> camera_link
    tf_camera = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['--x', '0.15', '--y', '0.0', '--z', '0.20',
                   '--yaw', '0', '--pitch', '0', '--roll', '0',
                   '--frame-id', 'base_link', '--child-frame-id', 'camera_link']
    )

    return LaunchDescription([
        realsense_launch,
        ldlidar_launch,
        tf_lidar,
        tf_camera
    ])
