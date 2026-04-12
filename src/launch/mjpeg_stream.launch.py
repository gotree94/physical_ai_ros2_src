from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([

        # 1) ESP32 MJPEG 영상 → CompressedImage 발행
        Node(
            package='myrosbot_one',
            executable='mjpeg_camera_publisher',
            name='mjpeg_camera_publisher',
            output='screen'
        ),

        # 2) Compressed → Raw 로 변환
        Node(
            package='image_transport',
            executable='republish',
            arguments=['compressed', 'raw'],
            remappings=[
                ('in/compressed', '/camera/image/compressed'),
                ('out', '/camera/image/uncompressed')
            ],
            output='screen',
        )
    ])
