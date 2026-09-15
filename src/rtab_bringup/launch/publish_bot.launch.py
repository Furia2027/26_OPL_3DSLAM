import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # Package Paths
    pkg_wheeltec_urdf = get_package_share_directory('wheeltec_robot_urdf')
    pkg_rtab_bringup = get_package_share_directory('rtab_bringup')

    # Resolve Gazebo resource search paths
    pkg_share_parent = os.path.dirname(pkg_wheeltec_urdf)
    models_path = os.path.join(pkg_rtab_bringup, 'gazebo', 'models')
    combined_gz_paths = f"{pkg_share_parent}:{models_path}"

    # Set Environment Variable for Gazebo Harmonic resources
    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=combined_gz_paths
    )

    # URDF path and Xacro dynamic evaluation
    urdf_file_path = os.path.join(pkg_wheeltec_urdf, 'urdf', 'oplsim.urdf')
    robot_desc = ParameterValue(
        Command(['xacro ', urdf_file_path]),
        value_type=str
    )

    # World path definition
    world_file_path = os.path.join(pkg_rtab_bringup, 'gazebo', 'restaurant.sdf')

    # 1. Gazebo Sim Launch
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file_path}'}.items()
    )

    # 2. Robot State Publisher Node
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

    # 3. ROS-Gazebo Bridge Node (Clock, Joint States, Cmd_Vel, Odom, TF, Camera)
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # System & Navigation Bridges
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            # Depth Camera (Orbbec Astra / rtab_cam) Bridges
            '/rtab_cam/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/rtab_cam/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/rtab_cam/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/rtab_cam/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked'
        ],
        output='screen'
    )

    # 4. Spawn Robot Entity in Gazebo Harmonic
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'wheeltec_oplbot',
            '-x', '0.5',
            '-y', '0.0',
            '-z', '0.25'
        ],
        output='screen'
    )

    return LaunchDescription([
        gz_resource_path,
        gz_sim,
        robot_state_publisher,
        ros_gz_bridge,
        spawn_robot
    ])
