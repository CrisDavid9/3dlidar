#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class StepperNode(Node):
    def __init__(self):
        super().__init__('stepper_control')

        self.publisher = self.create_publisher(
            Float64MultiArray,
            '/shaft_cont/commands',
            10
        )

        self.rad = 0.0
        self.step = 0
        self.max = 200
        self.min = 0
        self.dir = 'r'

        self.timer = self.create_timer(.5, self.timer_callback)

    def timer_callback(self):
        msg = Float64MultiArray()

        if (self.dir == 'r'):
            self.step += 1
            self.rad += 0.015708
        elif (self.dir == 'l'):
            self.step -= 1
            self.rad -= 0.015708

        if (self.step >= self.max):
            self.dir = 'l'
        elif (self.step <= self.min):
            self.dir = 'r'

        msg.data = [self.rad]

        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: {self.rad}')

def main():
    rclpy.init()
    node = StepperNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()