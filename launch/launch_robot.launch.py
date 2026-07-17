import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart

from launch_ros.actions import Node

def generate_launch_description():

    package_name='3dlidar'

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','3dlidar.launch.py'
                )]), launch_arguments={'use_sim_time': 'false', 'use_ros2_control': 'true'}.items()
    )

    robot_description = Command(['ros2 param get --hide-type /robot_state_publisher robot_description'])

    controller_params_file = os.path.join(get_package_share_directory(package_name),'config','my_controllers.yaml')

    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[{'robot_description': robot_description}, controller_params_file]
    )

    delayed_controller_manager = TimerAction(
        period=2.0, 
        actions=[controller_manager]
    )

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
        delayed_controller_manager,
        delay_spawners,
        delay_scanning
    ])