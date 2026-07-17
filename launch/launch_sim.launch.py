import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

def generate_launch_description():

    package_name='3dlidar'

    # Include the robot_state_publisher launch file
    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','3dlidar.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Include the Gazebo launch file
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
             )

    # Run the spawner node to place the robot in Gazebo
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', '3dlidar'],
                        output='screen')

    shaft_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["shaft_cont"]
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"]
    )

    delay_spawners = TimerAction(
        period=2.0,
        actions=[shaft_controller_spawner, joint_broad_spawner]
    )

    stepper_test = Node(
        package='3dlidar',
        executable='stepper_sim_node.py',
        name='stepper_control'
    )

    delay_stepper = TimerAction(
        period=3.0,
        actions=[stepper_test]
    )

    scanning_test = Node(
        package='3dlidar',
        executable='processing_node.py',
        name='scan_to_3d'
    )

    delay_scanning = TimerAction(
        period=3.0,
        actions=[scanning_test]
    )

    # Launch them all!
    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        delay_spawners,
        delay_stepper,
        delay_scanning
    ])