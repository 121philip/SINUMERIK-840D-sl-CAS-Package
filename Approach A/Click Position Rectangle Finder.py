import pyautogui
import keyboard  # For detecting key presses

print("Press 'q' to quit. Press 'c' to capture rectangle corners (press twice to define rectangle).")

points = []

while True:
    if keyboard.is_pressed('c'):
        x, y = pyautogui.position()
        points.append((x, y))
        print(f"Point {len(points)} captured: ({x}, {y})")

        # Wait until 'c' is released to avoid multiple captures
        while keyboard.is_pressed('c'):
            pass

        # When we have 2 points, calculate and print the rectangle
        if len(points) == 2:
            x1, y1 = points[0]
            x2, y2 = points[1]

            # Determine top-left and bottom-right coordinates
            top_left = (min(x1, x2), min(y1, y2))
            bottom_right = (max(x1, x2), max(y1, y2))
            top_right = (bottom_right[0], top_left[1])
            bottom_left = (top_left[0], bottom_right[1])

            print("\nRectangle coordinates:")
            print(f"Top-left: {top_left}")
            print(f"Top-right: {top_right}")
            print(f"Bottom-left: {bottom_left}")
            print(f"Bottom-right: {bottom_right}\n")

            # Reset points for new rectangle
            points = []

    if keyboard.is_pressed('q'):
        print("Exiting...")
        break
