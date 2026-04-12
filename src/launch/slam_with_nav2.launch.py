import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

	# myrosbot_one 패키지 경로
	pkg_path = get_package_share_directory('myrosbot_one')

	# Nav2 bringup launch 파일 경로
	nav2_bringup_path = get_package_share_directory('nav2_bringup')
	nav2_launch_file = os.path.join(
		nav2_bringup_path,
		'launch',
		'bringup_launch.py'
	)

	# config 파일 경로
	params_file = os.path.join(pkg_path, 'config', 'navigation.yaml')
	rviz_config = os.path.join(pkg_path, 'config', 'navigation.rviz')

	return LaunchDescription([

		# 1. Nav2 Bringup (SLAM 모드)
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(nav2_launch_file),
			launch_arguments={
				'slam': 'True',
				'params_file': params_file,
			}.items(),
		),

		# 2. RViz 실행
		Node(
			package='rviz2',
			executable='rviz2',
			name='rviz2',
			output='screen',
			arguments=['-d', rviz_config],
		),
	])