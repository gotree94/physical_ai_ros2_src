import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    package_name = 'myrosbot_one'

    # 패키지 디렉터리
    pkg_share_dir = get_package_share_directory(package_name)
    bringup_dir = get_package_share_directory('nav2_bringup')

    # Launch argument 선언
    map_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(os.environ['HOME'], 'maps', 'map.yaml'),
        description='Path to map file'
    )

    # 패키지 내부 설정 파일 경로
    navigation_params = os.path.join(pkg_share_dir, 'config', 'navigation.yaml')
    rviz_config_path = os.path.join(pkg_share_dir, 'config', 'navigation.rviz')

    # Nav2 bringup 실행 (SLAM 비활성화, 기존 맵 사용)
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'slam': 'False',
            'map': LaunchConfiguration('map'),
            'params_file': navigation_params,
        }.items()
    )

    # RViz 실행
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        output='screen'
    )

    return LaunchDescription([
        map_arg,
        nav2_bringup,
        rviz_node
    ])
