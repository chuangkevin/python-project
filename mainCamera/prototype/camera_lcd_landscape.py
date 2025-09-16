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
        draw.text((120, 120), "IMX708 Ready", fill="GREEN")
        disp.ShowImage(startup_image.rotate(90, expand=True))
        time.sleep(2)
        
        # Initialize Camera
        logging.info("Initializing IMX708 camera...")
        camera = Picamera2()
        
        # Configure camera for landscape display (320x240) with correct format
        config = camera.create_preview_configuration(
            main={"size": (320, 240), "format": "RGB888"},
            buffer_count=2
        )
        camera.configure(config)
        camera.start()
        
        # Wait for camera to stabilize
        time.sleep(2)
        
        logging.info("Starting camera preview on LCD (landscape)...")
        
        frame_count = 0
        start_time = time.time()
        fps = 0
        
        # Main camera loop - continuous operation
        while True:
            try:
                # Capture frame from camera
                frame = camera.capture_array()
                
                # Handle different frame formats
                if frame.shape[2] == 4:  # XBGR8888 format
                    # Extract RGB channels and swap order
                    rgb_frame = np.stack([
                        frame[:, :, 2],  # R from B channel
                        frame[:, :, 1],  # G from G channel
                        frame[:, :, 0]   # B from R channel
                    ], axis=-1)
                    image = Image.fromarray(rgb_frame, "RGB")
                elif frame.shape[2] == 3:  # RGB format
                    image = Image.fromarray(frame, "RGB")
                else:
                    # Grayscale
                    image = Image.fromarray(frame).convert("RGB")
                
                # Ensure correct size for landscape LCD (320x240)
                if image.size != (320, 240):
                    image = image.resize((320, 240), Image.LANCZOS)
                
                # Add overlay information (landscape oriented)
                draw = ImageDraw.Draw(image)
                
                # Calculate FPS every 30 frames
                frame_count += 1
                if frame_count % 30 == 0:
                    current_time = time.time()
                    fps = 30 / (current_time - start_time)
                    start_time = current_time
                
                # Add text overlay (positioned for landscape)
                draw.text((5, 5), f"FPS: {fps:.1f}", fill="YELLOW")
                draw.text((5, 25), "IMX708 Camera", fill="WHITE")
                draw.text((5, 45), "Landscape Mode", fill="CYAN")
                draw.text((200, 215), f"Frame: {frame_count}", fill="GREEN")
                
                # Rotate image 90 degrees clockwise for proper LCD orientation
                rotated_image = image.rotate(90, expand=True)
                
                # Display on LCD
                disp.ShowImage(rotated_image)
                
                if frame_count % 50 == 0:
                    logging.info(f"Displayed frame {frame_count}, FPS: {fps:.1f}")
                
                # Small delay for stability
                time.sleep(0.05)
                
            except KeyboardInterrupt:
                logging.info("Stopping by user request...")
                break
            except Exception as e:
                logging.error(f"Frame processing error: {e}")
                break
        
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
            # Show exit screen (landscape)
            exit_image = Image.new("RGB", (320, 240), "BLACK")
            draw = ImageDraw.Draw(exit_image)
            draw.text((130, 100), "Camera", fill="WHITE")
            draw.text((140, 120), "Test", fill="GREEN")
            draw.text((125, 140), "Complete!", fill="YELLOW")
            disp.ShowImage(exit_image.rotate(90, expand=True))
            time.sleep(3)
            disp.clear()
            logging.info("LCD cleared and test completed")
        except:
            pass

if __name__ == "__main__":
    main()