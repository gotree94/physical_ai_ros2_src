import sys
import termios
import tty
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class MyTeleopKeyboard(Node):
    def __init__(self):
        super().__init__('my_teleop_keyboard')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        self.linear_speed = 0.15    # m/s
        self.angular_speed = 0.8   # rad/s

        self.get_logger().info("Use W/S for forward/backward, A/D for rotation, Q to quit.")
        self.run()

    def get_key(self):
        """키보드에서 1글자 읽기 (blocking)"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

    def run(self):
        twist = Twist()
        while rclpy.ok():
            key = self.get_key()
            if key.lower() == 'w':
                twist.linear.x = self.linear_speed
                twist.angular.z = 0.0
            elif key.lower() == 's':
                twist.linear.x = -self.linear_speed
                twist.angular.z = 0.0
            elif key.lower() == 'a':
                twist.linear.x = 0.0
                twist.angular.z = self.angular_speed
            elif key.lower() == 'd':
                twist.linear.x = 0.0
                twist.angular.z = -self.angular_speed
            elif key.lower() == 'x':  # 정지
                twist.linear.x = 0.0
                twist.angular.z = 0.0
            elif key.lower() == 'q':
                self.get_logger().info("Exiting teleop...")
                break
            else:
                # 다른 키 누르면 정지
                twist.linear.x = 0.0
                twist.angular.z = 0.0

            self.publisher_.publish(twist)

def main():
    rclpy.init()
    node = MyTeleopKeyboard()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
