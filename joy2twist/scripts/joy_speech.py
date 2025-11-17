#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy, JointState
from rclpy.qos import qos_profile_sensor_data
from fbot_speech_msgs.srv import SynthesizeSpeech
from std_msgs.msg import Bool, Float64MultiArray
import numpy as np

BUTTON_Y = 3
BUTTON_X = 0
DPAD_VERTICAL = 5
DPAD_HORIZONTAL = 4

class JoystickSpeechNode(Node):
    def __init__(self):
        super().__init__('Joystick_Speech_node')
        self.initRosComm()

        self.last_DPAD_vertical_state = 0
        self.last_DPAD_horizontal_state = 0
        self.current_DPAD_vertical_state = 0
        self.current_DPAD_horizontal_state = 0

        self.horizontal_limit = 120.0, 240.0
        self.vertical_limit = 150.0, 190.0

        self.current_horizontal = 180.0
        self.current_vertical = 180.0
        self.start_pos()


    def initRosComm(self):
        self.joy_sub_ = self.create_subscription(Joy, 'joy', self.joy_cb, qos_profile_sensor_data)
        self.cli = self.create_client(SynthesizeSpeech, "/fbot_speech/ss/say_something")
        self.neck_pub_ = self.create_publisher(Float64MultiArray, "/updateNeck", 1)

    def start_pos(self):
        horizontal = self.current_horizontal
        vertical = self.current_vertical
        neck = Float64MultiArray()
        neck.data = [horizontal, vertical]
        self.neck_pub_.publish(neck)

        
    def joy_cb(self, joy_msg):
        

        self.current_DPAD_vertical_state = joy_msg.axes[DPAD_VERTICAL]
        self.current_DPAD_horizontal_state = joy_msg.axes[DPAD_HORIZONTAL]
        self.current_BUTTON_Y_state = joy_msg.buttons[BUTTON_Y]
        self.current_BUTTON_X_state = joy_msg.buttons[BUTTON_X]

        if self.current_BUTTON_Y_state == 1:
            self.get_logger().info("Botão Y pressionado")
            
            if self.current_DPAD_vertical_state == 1 and self.last_DPAD_vertical_state == 0:
                self.get_logger().info("Botão para cima pressionado")
                self.create_message('Hello my name is Boris', 'en')
            
            elif self.current_DPAD_vertical_state == -1 and self.last_DPAD_vertical_state == 0:
                self.get_logger().info("Botão para baixo pressionado")
                self.create_message('The FBOT is the Robotics Group at FURG (Federal University of Rio Grande) focused on developing projects in autonomous mobile robotics. ' \
                                'Their main objective is to prepare students for national and international competitions, applying knowledge in electronics, programming, and artificial intelligence.', 'en')
            
            elif self.current_DPAD_horizontal_state == 1 and self.last_DPAD_horizontal_state == 0:
                self.get_logger().info("Botão para direita pressionado")
                self.create_message('I come from FURG, the Federal University of Rio Grande, a public higher education institution recognized for its excellence in teaching, research, and outreach (extension).', 'en')
            
            elif self.current_DPAD_horizontal_state == -1 and self.last_DPAD_horizontal_state == 0:
                self.get_logger().info("Botão para esquerda pressionado")
                self.create_message('Currently, I am a four-time brazilian robotics competition champion. ', 'en')


        elif self.current_BUTTON_X_state == 1:
            self.get_logger().info("Botão X pressionado")
           
            if self.current_DPAD_vertical_state == 1 and self.current_vertical < self.vertical_limit:
                self.get_logger().info("Botão para cima pressionado")
                self.neck_movement(0.0, 1.0)
                
            elif self.current_DPAD_vertical_state == -1 and self.current_vertical > self.vertical_limit:
                self.get_logger().info("Botão para baixo pressionado")
                self.neck_movement(0.0, -1.0)

            elif self.current_DPAD_horizontal_state == 1 and self.current_horizontal > self.horizontal_limit:
                self.get_logger().info("Botão para direita pressionado")
                self.neck_movement(1.0, 0.0)

            elif self.current_DPAD_horizontal_state == -1 and self.current_horizontal < self.horizontal_limit:
                self.get_logger().info("Botão para esquerda pressionado")
                self.neck_movement(-1.0, 0.0)

        self.last_DPAD_horizontal_state = self.current_DPAD_horizontal_state
        self.last_DPAD_vertical_state = self.current_DPAD_vertical_state


    def neck_movement(self, horizontal_angle, vertical_angle):
        self.get_logger().info("Neck_movement ativado")
        self.current_horizontal += horizontal_angle
        self.current_vertical += vertical_angle
        neck = Float64MultiArray()
        neck.data = [self.current_horizontal, self.current_vertical]
        self.neck_pub_.publish(neck)
        

    def create_message(self, text, lang):
        self.get_logger().info('Creating message: "%s" in %s' % (text, lang))
        request = SynthesizeSpeech.Request()
        request.text = text
        request.lang = lang
        response = self.cli.call_async(request)
        #while response.done() is False:
        #   pass
        self.get_logger().info('Message created successfully!')


def main(args=None):
    rclpy.init(args=args)
    node = JoystickSpeechNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

