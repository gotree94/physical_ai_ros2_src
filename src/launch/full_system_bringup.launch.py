from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
import os

def generate_launch_description():

    pkg_name = 'myrosbot_one'

    # robot bringup launch 포함
    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory(pkg_name),
                'launch',
                'robot_bringup.launch.py'
            )
        )
    )

    # run executable
    camera_node = Node(
        package=pkg_name,
        executable='mjpeg_camera_publisher',
        name='mjpeg_camera_publisher',
        output='screen'
    )

    return LaunchDescription([
        bringup_launch,
        camera_node
    ])
