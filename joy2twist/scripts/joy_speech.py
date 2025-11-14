#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Joy
from rclpy.qos import qos_profile_sensor_data
from fbot_speech_msgs.srv import SynthesizeSpeech

class JoystickSpeechNode(Node):
    def __init__(self):
        super().__init__('Joystick_Speech_node')
        self.initRosComm()

        self.last_button_state_5 = 0
        self.last_button_state_4 = 0
        self.current_button_state_5 = 0
        self.current_button_state_4 = 0


    def initRosComm(self):
        self.joy_sub_ = self.create_subscription(Joy, 'joy', self.joy_cb, qos_profile_sensor_data)
        self.cli = self.create_client(SynthesizeSpeech, "/fbot_speech/ss/say_something")


    def joy_cb(self, joy_msg):

        self.current_button_state_5 = joy_msg.axes[5]
        self.current_button_state_4 = joy_msg.axes[4]

        if joy_msg.buttons[3] == 1:

            if self.current_button_state_5 == 1 and self.last_button_state_5 == 0:
                self.get_logger().info("Botão pressionado")
                self.create_message('Hello my name is Boris', 'en')

            elif self.current_button_state_5 == -1 and self.last_button_state_5 == 0:
                self.get_logger().info("Botão pressionado")
                self.create_message('The FBOT is the Robotics Group at FURG (Federal University of Rio Grande) focused on developing projects in autonomous mobile robotics. ' \
                                'Their main objective is to prepare students for national and international competitions, applying knowledge in electronics, programming, and artificial intelligence.', 'en')
            
            elif self.current_button_state_4 == 1 and self.last_button_state_4 == 0:
                self.get_logger().info("Botão pressionado")
                self.create_message('I come from FURG, the Federal University of Rio Grande, a public higher education institution recognized for its excellence in teaching, research, and outreach (extension).', 'en')

            elif self.current_button_state_4 == -1 and self.last_button_state_4 == 0:
                self.get_logger().info("Botão pressionado")
                self.create_message('Currently, I am a four-time brazilian robotics competition champion. ', 'en')

        self.last_button_state_4 = self.current_button_state_4
        self.last_button_state_5 = self.current_button_state_5

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

