#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import subprocess
import os

class AudioPlayerNode(Node):
    def __init__(self):
        super().__init__('audio_player_node')
        
        # Declare parameters
        self.declare_parameter('audio_device', 'default')
        self.audio_device = self.get_parameter('audio_device').value
        
        # Create subscriber
        self.subscription = self.create_subscription(
            String,
            'play_audio',
            self.audio_callback,
            10
        )
        
        self.get_logger().info(f'Audio Player Node started with device: {self.audio_device}')
        self.list_audio_devices()
    
    def play_audio(self, file_path):
        """Play audio file using afplay (macOS) or aplay (Linux)"""
        if not os.path.exists(file_path):
            self.get_logger().error(f'Audio file not found: {file_path}')
            return False
        
        try:
            self.get_logger().info(f'Playing: {file_path}')
            
            # Detect OS and use appropriate player
            import platform
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['afplay', file_path], check=True)
            else:  # Linux (Pi)
                if self.audio_device == 'default':
                    subprocess.run(['aplay', file_path], check=True)
                else:
                    subprocess.run(['aplay', '-D', self.audio_device, file_path], check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.get_logger().error(f'Error playing audio: {e}')
            return False
        except FileNotFoundError:
            self.get_logger().error('Audio player not found. macOS uses afplay (built-in), Linux needs: sudo apt install alsa-utils')
            return False
    
    def play_mp3(self, file_path):
        """Play MP3 file using mpg123"""
        try:
            subprocess.run(['mpg123', file_path], check=True)
            return True
        except subprocess.CalledProcessError as e:
            self.get_logger().error(f'Error playing MP3: {e}')
            return False
        except FileNotFoundError:
            self.get_logger().error('mpg123 not found. Install with: sudo apt install mpg123')
            return False
    
    def audio_callback(self, msg):
        """Callback for audio playback requests"""
        file_path = msg.data
        
        if file_path.endswith('.mp3'):
            self.play_mp3(file_path)
        else:
            self.play_audio(file_path)
    
    def list_audio_devices(self):
        """List available audio devices"""
        try:
            result = subprocess.run(['aplay', '-l'], 
                                  capture_output=True, text=True)
            self.get_logger().info(f'Available audio devices:\n{result.stdout}')
        except Exception as e:
            self.get_logger().error(f'Error listing devices: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = AudioPlayerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()