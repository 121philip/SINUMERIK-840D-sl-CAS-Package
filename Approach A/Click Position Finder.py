import pyautogui
import keyboard  # For detecting key presses

print("Press 'q' to quit. Press 'c' to capture the mouse coordinates.")

while True:
    if keyboard.is_pressed('c'):
        x, y = pyautogui.position()
        print(f"Mouse position: ({x}, {y})")
        while keyboard.is_pressed('c'):
            pass  # Wait until 'c' is released to avoid multiple prints
    if keyboard.is_pressed('q'):
        print("Exiting...")
        break
