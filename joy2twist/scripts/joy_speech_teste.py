#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from fbot_speech_msgs.srv import SynthesizeSpeech 

class SpeechServer(Node):
    def __init__(self):
        super().__init__('speech_server_node')

        self.srv = self.create_service(
            SynthesizeSpeech, 
            'speech_msg', 
            self.synthesize_speech_callback
        )
        self.get_logger().info("Serviço 'speech_msg' (SynthesizeSpeech) iniciado e pronto.")

    def synthesize_speech_callback(self, request, response):
        
        self.get_logger().info("--- REQUISIÇÃO RECEBIDA ---")
        self.get_logger().info(f"Texto: '{request.text}'")
        self.get_logger().info(f"Idioma: '{request.lang}'")

        return response

def main(args=None):
    rclpy.init(args=args)
    speech_server = SpeechServer()
    rclpy.spin(speech_server)
    speech_server.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()