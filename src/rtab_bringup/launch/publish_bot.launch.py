import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_wheeltec_urdf = get_package_share_directory('wheeltec_robot_urdf')
    pkg_rtab_bringup = get_package_share_directory('rtab_bringup')

    pkg_share_parent = os.path.dirname(pkg_wheeltec_urdf)
    models_path = os.path.join(pkg_rtab_bringup, 'gazebo', 'models')
    combined_gz_paths = f"{pkg_share_parent}:{models_path}"

    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=combined_gz_paths
    )

    urdf_file_path = os.path.join(pkg_wheeltec_urdf, 'urdf', 'oplsim.urdf')
    robot_desc = ParameterValue(
        Command(['xacro ', urdf_file_path]),
        value_type=str
    )

    world_file_path = os.path.join(pkg_rtab_bringup, 'gazebo', 'restaurant.sdf')

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file_path}'}.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True
        }]
    )

    # REMOVED /tf from bridge arguments to give EKF total control of odom -> base_footprint
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/rtab_cam/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/rtab_cam/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/rtab_cam/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/rtab_cam/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked'
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # Optimized IMU configuration for stable 2D EKF fusion
    robot_localization_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'frequency': 30.0,
            'two_d_mode': True,
            'publish_tf': True,
            'odom_frame': 'odom',
            'base_link_frame': 'base_footprint',
            'world_frame': 'odom',
            'odom0': '/odom',
            'odom0_config': [True, True, False,
                            False, False, True,
                            True, True, False,
                            False, False, True,
                            False, False, False],
            'imu0': '/imu',
            'imu0_config': [False, False, False,
                           False, False, True,     # Fuse Yaw angle only
                           False, False, False,
                           False, False, True,     # Fuse Yaw angular velocity
                           False, False, False],    # Fuse X-axis linear acceleration
            'imu0_differential': False,
            'imu0_relative': True
        }]
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'wheeltec_oplbot',
            '-x', '0.5',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen'
    )

    return LaunchDescription([
        gz_resource_path,
        gz_sim,
        robot_state_publisher,
        ros_gz_bridge,
        robot_localization_node,
        spawn_robot
    ])
