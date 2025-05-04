import pyautogui
import cv2
import numpy as np
import pytesseract
from PIL import Image
import time
from pynput import mouse
from opcua import Client
import threading

# OPC UA Configuration - X130 Company network
OPC_URL = "opc.tcp://192.168.100.1:4840"
START_NODE = "ns=2;s=/Plc/DB21.DBX7.1"
STOP_NODE = "ns=2;s=/Plc/DB21.DBX7.3"
RESET_NODE = "ns=2;s=/Plc/DB21.DBX7.7"
OPC_USER = "OpcUaClient"
OPC_PASSWORD = "SUNRISE"

# Define the screen resolution and button areas
SCREEN_WIDTH, SCREEN_HEIGHT = 2560, 1600

START_BUTTON_AREA = {
    "x_min": 664,  # Left boundary of the START button (adjust as needed)
    "x_max": 721,  # Right boundary of the START button
    "y_min": 84,  # Top boundary of the START button
    "y_max": 183  # Bottom boundary of the START button
}

STOP_BUTTON_AREA = {
    "x_min": 783,  # Left boundary of the STOP button (adjust as needed)
    "x_max": 840,  # Right boundary of the STOP button
    "y_min": 84,  # Top boundary of the STOP button
    "y_max": 183  # Bottom boundary of the STOP button
}

RESET_BUTTON_AREA = {
    "x_min": 843,  # Left boundary of the RESET button (adjust as needed)
    "x_max": 921,  # Right boundary of the RESET button
    "y_min": 84,  # Top boundary of the RESET button
    "y_max": 183  # Bottom boundary of the RESET button
}


def send_opc_signal(node_id, value=True):
    """Send signal to OPC UA server"""
    try:
        client = Client(OPC_URL)
        client.set_user(OPC_USER)
        client.set_password(OPC_PASSWORD)
        client.connect()
        node = client.get_node(node_id)
        node.set_value(value)
        print(f"OPC Signal sent to {node_id}: {value}")
        client.disconnect()
    except Exception as e:
        print(f"OPC Error: {e}")


def delayed_start():
    """Handle delayed start with 2-second wait"""
    print("Delayed start initiated...")
    time.sleep(4)
    send_opc_signal(START_NODE)


def is_within_button_area(x, y, button_area):
    return (
            button_area["x_min"] <= x <= button_area["x_max"] and
            button_area["y_min"] <= y <= button_area["y_max"]
    )


def on_click(x, y, button, pressed):
    if pressed:
        if is_within_button_area(x, y, START_BUTTON_AREA):
            print("Simulation START detected - triggering delayed OPC start")
            threading.Thread(target=delayed_start).start()
        elif is_within_button_area(x, y, STOP_BUTTON_AREA):
            print("Simulation STOP detected - triggering OPC stop")
            send_opc_signal(STOP_NODE)
        elif is_within_button_area(x, y, RESET_BUTTON_AREA):
            print("Simulation RESET detected - triggering OPC reset")
            send_opc_signal(RESET_NODE)


def detect_collision_window():
    """Monitor for collision popups (existing functionality)"""
    while True:
        # Take a screenshot of the current screen
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        # Convert the screenshot to grayscale for better OCR
        gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)

        # Extract text from the image using OCR
        text = pytesseract.image_to_string(gray)

        # Check if the collision message appears
        if "Tool/Part collision found" in text:
            print("Collision detected! Triggering emergency stop")
            send_opc_signal(STOP_NODE)

        # Add a small delay to reduce CPU usage
        time.sleep(0.5)


if __name__ == "__main__":
    # OCR configuration
    pytesseract.pytesseract.tesseract_cmd = r"D:\Program Files\Tesseract-OCR\tesseract.exe"

    # Start collision detection in a separate thread
    collision_thread = threading.Thread(target=detect_collision_window, daemon=True)
    collision_thread.start()

    # Start the mouse event listener
    print("Monitoring for collision pop-up and button clicks...")
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
