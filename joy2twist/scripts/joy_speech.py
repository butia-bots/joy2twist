#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy, JointState
from rclpy.qos import qos_profile_sensor_data
from fbot_speech_msgs.srv import SynthesizeSpeech
from std_msgs.msg import Bool, Float64MultiArray

BUTTON_Y = 3
BUTTON_X = 2
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


    def initRosComm(self):
        self.joy_sub_ = self.create_subscription(Joy, 'joy', self.joy_cb, qos_profile_sensor_data)
        self.cli = self.create_client(SynthesizeSpeech, "/fbot_speech/ss/say_something")
        self.neck_pub_ = self.create_publisher(Float64MultiArray, "/updateNeck", 1)
        self.joint_sub_ = self.create_subscription(JointState, "/boris_head/joint_states", self.joint_cb, qos_profile_sensor_data)

    def joint_cb(self, msg: JointState):
        self.get_logger().info("Recebendo joint states")
        self.joint = msg
        self.joint.position = msg.position
        self.get_logger().info(str(self.joint.position))

        
    def joy_cb(self, joy_msg):

        self.current_DPAD_vertical_state = joy_msg.axes[DPAD_VERTICAL]
        self.current_DPAD_horizontal_state = joy_msg.axes[DPAD_HORIZONTAL]
        self.current_BUTTON_Y_state = joy_msg.buttons[BUTTON_Y]
        self.current_BUTTON_X_state = joy_msg.buttons[BUTTON_X]

        if self.current_BUTTON_Y_state == 1:
            
            #cima
            if self.current_DPAD_vertical_state == 1 and self.last_DPAD_vertical_state == 0:
                self.get_logger().info("Botão pressionado")
                self.create_message('Hello my name is Boris', 'en')
            
            #baixo
            elif self.current_DPAD_vertical_state == -1 and self.last_DPAD_vertical_state == 0:
                self.get_logger().info("Botão pressionado")
                self.create_message('The FBOT is the Robotics Group at FURG (Federal University of Rio Grande) focused on developing projects in autonomous mobile robotics. ' \
                                'Their main objective is to prepare students for national and international competitions, applying knowledge in electronics, programming, and artificial intelligence.', 'en')
            
            #direita
            elif self.current_DPAD_horizontal_state == 1 and self.last_DPAD_horizontal_state == 0:
                self.get_logger().info("Botão pressionado")
                self.create_message('I come from FURG, the Federal University of Rio Grande, a public higher education institution recognized for its excellence in teaching, research, and outreach (extension).', 'en')
            
            #esquerda
            elif self.current_DPAD_horizontal_state == -1 and self.last_DPAD_horizontal_state == 0:
                self.get_logger().info("Botão pressionado")
                self.create_message('Currently, I am a four-time brazilian robotics competition champion. ', 'en')


        elif self.current_BUTTON_X_state == 1:
           
           #cima
            if self.current_DPAD_vertical_state == 1 and self.last_DPAD_vertical_state == 0:
                self.get_logger().info("Botão para cima pressionado")
                
            #baixo
            elif self.current_DPAD_vertical_state == -1 and self.last_DPAD_vertical_state == 0:
                self.get_logger().info("Botão para baixo pressionado")
                
            #direita
            elif self.current_DPAD_horizontal_state == 1 and self.last_DPAD_horizontal_state == 0:
                self.get_logger().info("Botão para direita pressionado")
                
            #esquerda
            elif self.current_DPAD_horizontal_state == -1 and self.last_DPAD_horizontal_state == 0:
                self.get_logger().info("Botão para esquerda pressionado")
                


        self.last_DPAD_horizontal_state = self.current_DPAD_horizontal_state
        self.last_DPAD_vertical_state = self.current_DPAD_vertical_state

    def neck_movement(self, x_angle, z_angle):
        neck = Float64MultiArray.Request()
        neck.data = [x_angle, z_angle]

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

