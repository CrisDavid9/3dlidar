#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, JointState, PointCloud2
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Float64, Float64MultiArray
import math

class ScanTo3D(Node):
    def __init__(self):
        super().__init__('scan_to_3d')

        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_cb, 2)

        #self.angle_sub = self.create_subscription(
            #Float64MultiArray, '/shaft_cont/commands', self.angle_cb, 10)
        
        self.angle_sub = self.create_subscription(
            JointState, '/joint_states', self.angle_cb, 2)

        self.cloud_pub = self.create_publisher(PointCloud2, '/points3d', 2)

        self.tilt_angle = 0.0
        self.points = []

    def angle_cb(self, msg):
        #self.tilt_angle = msg.data[0]
        idx = msg.name.index('shaft_joint')
        self.tilt_angle = msg.position[idx]

    def scan_cb(self, scan: LaserScan):
        self.points.clear()
        angle = scan.angle_min

        for r in scan.ranges:
            if r < scan.range_min or r > scan.range_max:
                angle += scan.angle_increment
                continue

            # 2D lidar frame
            x = r * math.cos(angle)
            y = r * math.sin(angle)

            # lift into 3D using tilt angle
            z = y * math.sin(-self.tilt_angle)
            y = y * math.cos(-self.tilt_angle)

            self.points.append((x, y, z))

            angle += scan.angle_increment

        cloud_msg = point_cloud2.create_cloud_xyz32(
            scan.header,
            self.points
        )

        self.cloud_pub.publish(cloud_msg)

def main():
    rclpy.init()
    node = ScanTo3D()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()