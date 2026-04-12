import rclpy
from rclpy.node import Node
from std_msgs.msg import Int64MultiArray
from rclpy.qos import QoSProfile, ReliabilityPolicy

class EncoderGyroSub(Node):
    def __init__(self):
        super().__init__('encoder_listener')
        qos = QoSProfile(depth=10)
        qos.reliability = ReliabilityPolicy.BEST_EFFORT  # <-- effort mode 맞춤
        self.sub = self.create_subscription(
            Int64MultiArray,
            'encoder_deltas_gyroz_bat_rssi',
            self.callback,
            qos
        )

    def callback(self, msg):
        deltas = list(msg.data)
        self.get_logger().info(f'Encoder deltas: {deltas}')

def main():
    rclpy.init()
    node = EncoderGyroSub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()