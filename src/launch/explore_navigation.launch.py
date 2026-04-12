from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import ThisLaunchFileDir
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    # navigation.yaml 위치
    nav_params = '/root/myros_ws/install/myrosbot_one/share/myrosbot_one/config/navigation.yaml'

    # rviz config
    rviz_config = '/root/myros_ws/install/myrosbot_one/share/myrosbot_one/config/navigation.rviz'

    # explore params
    explore_params = '/root/uros_ws/src/m-explore-ros2/explore/config/params.yaml'

    # nav2 bringup
    bringup_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch',
                'bringup_launch.py')]),
        launch_arguments={
            'slam': 'True',
            'params_file': nav_params
        }.items()
    )

    # rviz2
    rviz_cmd = ExecuteProcess(
        cmd=['rviz2', '-d', rviz_config],
        output='screen'
    )

    # explore_lite
    explore_cmd = Node(
        package='explore_lite',
        executable='explore',
        output='screen',
        parameters=[explore_params]
    )

    return LaunchDescription([
        bringup_cmd,
        rviz_cmd,
        explore_cmd
    ])
