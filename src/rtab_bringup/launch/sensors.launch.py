import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    astra_pkg = get_package_share_directory('astra_camera')
    ldlidar_pkg = get_package_share_directory('ldlidar_node')
    rtabmap_pkg = get_package_share_directory('rtabmap_launch')

    # Orbbec DaBai Launch
    dabai_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(astra_pkg, 'launch', 'dabai.launch.py')
        )
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
        dabai_launch,
        ldlidar_launch,
        tf_lidar,
        tf_camera
    ])
