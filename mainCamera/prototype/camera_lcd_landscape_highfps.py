#!/usr/bin/env python3

import os
import sys
import time
import logging
import numpy as np
sys.path.append("..")

from lib import LCD_2inch4
from PIL import Image, ImageDraw, ImageFont
from picamera2 import Picamera2

# Setup logging
logging.basicConfig(level=logging.INFO)

def main():
    try:
        # Initialize LCD
        logging.info("Initializing 2.4inch LCD...")
        disp = LCD_2inch4.LCD_2inch4()
        disp.Init()
        disp.clear()
        
        # Show startup screen (landscape)
        startup_image = Image.new("RGB", (320, 240), "BLACK")
        draw = ImageDraw.Draw(startup_image)
        draw.text((100, 100), "Camera Starting...", fill="WHITE")
        draw.text((110, 120), "High FPS Mode", fill="GREEN")
        disp.ShowImage(startup_image.rotate(90, expand=True))
        time.sleep(2)
        
        # Initialize Camera
        logging.info("Initializing IMX708 camera...")
        camera = Picamera2()
        
        # High performance configuration
        config = camera.create_preview_configuration(
            main={"size": (320, 240), "format": "RGB888"},
            buffer_count=4,  # Increased buffer for smoother streaming
            queue=False     # Disable queueing for lower latency
        )
        
        # Set camera controls for better performance
        camera.configure(config)
        
        # Optimize camera settings for high FPS
        controls = {
            "FrameRate": 30,           # Target 30 FPS
            "ExposureTime": 8000,      # Shorter exposure for faster capture
            "AnalogueGain": 2.0,       # Higher gain to compensate for shorter exposure
            "AeEnable": False,         # Disable auto exposure for consistent timing
            "AwbEnable": False,        # Disable auto white balance for performance
        }
        camera.set_controls(controls)
        
        camera.start()
        
        # Wait for camera to stabilize
        time.sleep(1)  # Reduced startup time
        
        logging.info("Starting high-FPS camera preview on LCD...")
        
        frame_count = 0
        start_time = time.time()
        fps = 0
        last_fps_time = time.time()
        
        # Pre-create font for better performance (optional)
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Main camera loop - optimized for high FPS
        while True:
            try:
                # Capture frame from camera (non-blocking)
                frame = camera.capture_array()
                
                # Fast format conversion
                if frame.shape[2] == 4:  # XBGR8888 format
                    # Optimized RGB extraction using numpy slicing
                    rgb_frame = frame[:, :, [2, 1, 0]]  # BGR to RGB swap
                    image = Image.fromarray(rgb_frame, "RGB")
                else:
                    image = Image.fromarray(frame, "RGB")
                
                # Resize only if necessary
                if image.size != (320, 240):
                    image = image.resize((320, 240), Image.NEAREST)  # Faster resize method
                
                frame_count += 1
                
                # Update FPS calculation less frequently for better performance
                current_time = time.time()
                if current_time - last_fps_time >= 1.0:  # Update every second
                    fps = frame_count / (current_time - start_time)
                    last_fps_time = current_time
                
                # Add minimal overlay (only every 10th frame to save processing)
                if frame_count % 10 == 0:
                    draw = ImageDraw.Draw(image)
                    draw.text((5, 5), f"FPS: {fps:.1f}", fill="YELLOW")
                    draw.text((5, 25), "High Performance", fill="CYAN")
                    draw.text((200, 215), f"{frame_count}", fill="GREEN")
                
                # Rotate image 90 degrees clockwise
                rotated_image = image.rotate(90, expand=True)
                
                # Display on LCD
                disp.ShowImage(rotated_image)
                
                # Minimal delay for maximum FPS
                # No sleep to achieve highest possible framerate
                
                # Progress logging (less frequent)
                if frame_count % 300 == 0:  # Every 300 frames (10 seconds at 30fps)
                    logging.info(f"Displayed {frame_count} frames, Current FPS: {fps:.1f}")
                
            except KeyboardInterrupt:
                logging.info("Stopping by user request...")
                break
            except Exception as e:
                logging.error(f"Frame processing error: {e}")
                # Continue on error instead of breaking for better stability
                time.sleep(0.01)
                continue
        
    except Exception as e:
        logging.error(f"Setup error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        try:
            camera.stop()
            logging.info("Camera stopped")
        except:
            pass
        
        try:
            # Show exit screen
            exit_image = Image.new("RGB", (320, 240), "BLACK")
            draw = ImageDraw.Draw(exit_image)
            draw.text((120, 100), "High FPS", fill="WHITE")
            draw.text((140, 120), "Test", fill="GREEN")
            draw.text((125, 140), "Complete!", fill="YELLOW")
            draw.text((100, 160), f"Final FPS: {fps:.1f}", fill="CYAN")
            disp.ShowImage(exit_image.rotate(90, expand=True))
            time.sleep(3)
            disp.clear()
            logging.info("LCD cleared and test completed")
        except:
            pass

if __name__ == "__main__":
    main()