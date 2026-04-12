import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():

    # 사용자 홈 디렉터리 기준 maps 디렉터리
    home_dir = os.path.expanduser("~")
    map_dir = os.path.join(home_dir, "maps")
    os.makedirs(map_dir, exist_ok=True)  # maps 디렉터리가 없으면 생성

    # 저장될 지도 파일 경로
    default_map_path = os.path.join(map_dir, "map")

    # launch 인자로 map 경로를 받을 수 있도록 설정
    map_arg = DeclareLaunchArgument(
        'map',
        default_value=default_map_path,
        description='Path to save the map'
    )

    # map_saver_cli 실행 노드
    map_saver_node = Node(
        package='nav2_map_server',
        executable='map_saver_cli',
        name='map_saver',
        output='screen',
        arguments=[
            '-f', LaunchConfiguration('map'),
            '--ros-args', '-p', 'save_map_timeout:=60.0'
        ]
    )

    return LaunchDescription([
        map_arg,
        map_saver_node
    ])
