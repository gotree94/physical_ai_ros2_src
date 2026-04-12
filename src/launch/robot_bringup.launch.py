import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

def generate_launch_description():

    package_name='myrosbot_one'

    rsp=IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    os.path.join(
                        get_package_share_directory(package_name),
                        'launch',
                        'rsp.launch.py')]), 
                launch_arguments={'use_sim_time': 'true'}.items()
    )

    
    micro_ros=Node(
            package='micro_ros_agent',
            executable='micro_ros_agent',
            name='micro_ros_agent_udp',
            output='screen',
            arguments=['udp4', '--port', '8888', '-v4']    
    )
    
    joint_pub=Node(
            package='myrosbot_one',
            executable='robot_telemetry_publisher',
            name='robot_telemetry_publisher',
            #output='log'
            arguments=['--ros-args', '--log-level', 'WARN'],
    ) 

    lidar_pub=Node(
            package='myrosbot_one',   # 패키지 이름
            executable='lidar_publisher', # 실행 파일 이름 (ros2 run 뒤의 이름)
            name='lidar_publisher',       # 노드 이름 (선택사항)
            #output='log'               # 터미널에 출력 보이도록
            arguments=['--ros-args', '--log-level', 'WARN'],
    )

    return LaunchDescription([
        micro_ros,
        joint_pub,
        lidar_pub,
        rsp,
    ])