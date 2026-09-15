import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    rtabmap_launch_dir = get_package_share_directory('rtabmap_launch')

    localization_arg = DeclareLaunchArgument(
        'localization',
        default_value='false',
        description='Set to true for pure localization mode using existing map database.'
    )

    # Shared topic parameters matching your active ROS 2 topics
    common_args = {
        'rgb_topic': '/camera/color/image_raw',
        'depth_topic': '/camera/depth/image_raw',
        'camera_info_topic': '/camera/color/camera_info',
        'scan_topic': '/ldlidar_node/scan',
        'subscribe_scan': 'true',
        'frame_id': 'base_link',
        'approx_sync': 'true',
        'use_sim_time': 'false',
        'qos': '2',
        'qos_camera_info': '2',
    }

    # Mapping Mode (Creates/clears map)
    mapping_mode = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(rtabmap_launch_dir, 'launch', 'rtabmap.launch.py')
        ),
        condition=UnlessCondition(LaunchConfiguration('localization')),
        launch_arguments={
            **common_args,
            'rtabmap_args': '--delete_db_on_start',
        }.items()
    )

    # Localization Mode (Loads existing map without updating)
    localization_mode = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(rtabmap_launch_dir, 'launch', 'rtabmap.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('localization')),
        launch_arguments={
            **common_args,
            'rtabmap_args': 'Mem/IncrementalMemory:=false Mem/InitWMWithAllNodes:=true',
        }.items()
    )

    return LaunchDescription([
        localization_arg,
        mapping_mode,
        localization_mode
    ])
