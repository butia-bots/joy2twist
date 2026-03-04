#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from rclpy.qos import qos_profile_sensor_data
from fbot_speech_msgs.srv import SynthesizeSpeech
from std_msgs.msg import Float64MultiArray
import yaml


class JoystickSpeechNode(Node):
    def __init__(self):
        super().__init__('Joystick_Speech_node')

        self.enable_logs = False

        self.yaml_opener()
        self.load_parameters()
        self.initRosComm()

        self.last_DPAD_vertical_state = 0
        self.last_DPAD_horizontal_state = 0
        self.current_DPAD_vertical_state = 0
        self.current_DPAD_horizontal_state = 0

        self.current_horizontal = self.initial_horizontal
        self.current_vertical = self.initial_vertical

        self.start_pos()

    def yaml_opener(self):
        with open("/home/fbot/fbot_ws/src/joy2twist/joy2twist/config/joyinterface.yaml", "r") as file:
            self.safe_build = yaml.safe_load(file)


    def initRosComm(self):
        self.joy_sub_ = self.create_subscription(Joy, 'joy', self.joy_cb, qos_profile_sensor_data)
        self.cli = self.create_client(SynthesizeSpeech, "/fbot_speech/ss/say_something")
        self.neck_pub_ = self.create_publisher(Float64MultiArray, "/updateNeck", 1)

    def start_pos(self):
        self.current_horizontal = self.initial_horizontal
        self.current_vertical = self.initial_vertical
        neck = Float64MultiArray()
        neck.data = [self.initial_horizontal, self.initial_vertical]
        self.neck_pub_.publish(neck)


    def joy_cb(self, joy_msg):

        self.current_BUTTON_Y_state = joy_msg.buttons[self.BUTTON_Y]
        self.current_BUTTON_X_state = joy_msg.buttons[self.BUTTON_X]
        self.current_BUTTON_A_state = joy_msg.buttons[self.BUTTON_A]
        self.current_DPAD_vertical_state = joy_msg.axes[self.DPAD_VERTICAL]
        self.current_DPAD_horizontal_state = joy_msg.axes[self.DPAD_HORIZONTAL]


        if self.current_BUTTON_Y_state == 1:
            if self.enable_logs: self.get_logger().info(f"BUTTON Y pressionado - Modo Fala Ativado. {self.current_DPAD_vertical_state}")

            if self.current_DPAD_vertical_state == 1 and self.last_DPAD_vertical_state == 0:
                if self.enable_logs: self.get_logger().info("SPEECH - Botão para cima pressionado")
                self.create_message(self.up_message_text, self.up_message_lang)

            elif self.current_DPAD_vertical_state == -1 and self.last_DPAD_vertical_state == 0:
                if self.enable_logs: self.get_logger().info("SPEECH - Botão para baixo pressionado")
                self.create_message(self.down_message_text, self.down_message_lang)

            elif self.current_DPAD_horizontal_state == 1 and self.last_DPAD_horizontal_state == 0:
                if self.enable_logs: self.get_logger().info("SPEECH - Botão para direita pressionado")
                self.create_message(self.left_message_text, self.left_message_lang)

            elif self.current_DPAD_horizontal_state == -1 and self.last_DPAD_horizontal_state == 0:
                if self.enable_logs: self.get_logger().info("SPEECH - Botão para esquerda pressionado")
                self.create_message(self.right_message_text, self.right_message_lang)


        elif self.current_BUTTON_X_state == 1:

            if self.current_DPAD_vertical_state == 1 and self.current_vertical < self.up_limit:
                if self.enable_logs: self.get_logger().info("NECK - Botão para cima pressionado")
                self.neck_movement(0.0, self.velocity)

            elif self.current_DPAD_vertical_state == -1 and self.current_vertical > self.down_limit:
                if self.enable_logs: self.get_logger().info("NECK - Botão para baixo pressionado")
                self.neck_movement(0.0, -self.velocity)

            elif self.current_DPAD_horizontal_state == 1 and self.current_horizontal < self.right_limit:
                if self.enable_logs: self.get_logger().info("NECK - Botão para esquerda pressionado")
                self.neck_movement(self.velocity, 0.0)

            elif self.current_DPAD_horizontal_state == -1 and self.current_horizontal > self.left_limit:
                if self.enable_logs: self.get_logger().info("NECK - Botão para direita pressionado")
                self.neck_movement(-self.velocity, 0.0)

            elif self.current_BUTTON_A_state == 1:
                self.start_pos()

        self.last_DPAD_horizontal_state = self.current_DPAD_horizontal_state
        self.last_DPAD_vertical_state = self.current_DPAD_vertical_state


    def neck_movement(self, horizontal_angle, vertical_angle):
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
        if not self.cli.wait_for_service(5):
            self.get_logger().error("Service not available")
            return
        response = self.cli.call_async(request)
        #while response.done() is False:
        #   pass
        self.get_logger().info('Message created successfully!')


    def load_parameters(self):
        self.up_limit = self.safe_build["neck_limits"]["up_limit"]
        self.down_limit = self.safe_build["neck_limits"]["down_limit"]
        self.right_limit = self.safe_build["neck_limits"]["right_limit"]
        self.left_limit = self.safe_build["neck_limits"]["left_limit"]

        self.velocity = self.safe_build["neck_velocity_factor"]["velocity"]

        self.initial_horizontal = self.safe_build["neck_initial_position"]["initial_horizontal"]
        self.initial_vertical = self.safe_build["neck_initial_position"]["initial_vertical"]

        self.BUTTON_Y = self.safe_build["button_index_map"]["button"]["enable_speech"]
        self.BUTTON_X = self.safe_build["button_index_map"]["button"]["enable_neck_movement"]
        self.BUTTON_A = self.safe_build["button_index_map"]["button"]["centralize_neck"]
        self.DPAD_VERTICAL = self.safe_build["button_index_map"]["axis"]["vertical_movement"]
        self.DPAD_HORIZONTAL = self.safe_build["button_index_map"]["axis"]["horizontal_movement"]

        self.up_message_text = self.safe_build["bot_message"]["up"]["text"]
        self.up_message_lang = self.safe_build["bot_message"]["up"]["lang"]
        self.down_message_text = self.safe_build["bot_message"]["down"]["text"]
        self.down_message_lang = self.safe_build["bot_message"]["down"]["lang"]
        self.left_message_text = self.safe_build["bot_message"]["left"]["text"]
        self.left_message_lang = self.safe_build["bot_message"]["left"]["lang"]
        self.right_message_text = self.safe_build["bot_message"]["right"]["text"]
        self.right_message_lang = self.safe_build["bot_message"]["right"]["lang"]


def main(args=None):
    rclpy.init(args=args)
    node = JoystickSpeechNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
