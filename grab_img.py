"""
Usage: Run script then hold CTRL anywhere on screen to drag a box around desired screen capture area.
"""

import win32gui
import win32api
import win32con
from ctypes import windll
from time import sleep
from PIL import ImageGrab, ImageTk, Image, ImageChops, ImageOps


"""
# grab_screen()
# Purpose: Save a PIL image of the appropriate area of the screen
# Arguments: None
# Returns: PIL image
"""
def grab_screen():
    while True:                                                         # Loop until return
        # Declare variable for future cursor
        cursor_current_x, cursor_current_y = 0, 0
        # Declare boolean for cropping later
        crop_im = False

        # Get device context
        win_DC = win32gui.GetDC(0)
        cursor_origin_x, cursor_origin_y = win32gui.GetCursorPos()      # Get cursor position
        full_image = ImageGrab.grab(bbox=(0,                            # Capture entire screen
                                          0,
                                          win32api.GetSystemMetrics(0),
                                          win32api.GetSystemMetrics(1)))

        # While CTRL key is pressed
        while win32api.GetAsyncKeyState(win32con.VK_CONTROL) < 0:
            if not crop_im:
                # Set crop bool so crop branch is entered after
                crop_im = True

            # Get current cursor position
            cursor_current_x, cursor_current_y = win32gui.GetCursorPos()
            # Draw a box with original cursor
            win32gui.MoveToEx(win_DC, cursor_origin_x, cursor_origin_y)
            # and current cursor as opposite corners
            win32gui.LineTo(win_DC, cursor_origin_x, cursor_current_y)
            win32gui.MoveToEx(win_DC, cursor_origin_x, cursor_current_y)
            win32gui.LineTo(win_DC, cursor_current_x, cursor_current_y)
            win32gui.MoveToEx(win_DC, cursor_current_x, cursor_current_y)
            win32gui.LineTo(win_DC, cursor_current_x, cursor_origin_y)
            win32gui.MoveToEx(win_DC, cursor_current_x, cursor_origin_y)
            win32gui.LineTo(win_DC, cursor_origin_x, cursor_origin_y)

        if crop_im:                                                     # Enter crop branch, crop to box size
            cropped_image = full_image.crop((min(cursor_current_x, cursor_origin_x),
                                             min(cursor_current_y,
                                                 cursor_origin_y),
                                             max(cursor_current_x,
                                                 cursor_origin_x),
                                             max(cursor_current_y, cursor_origin_y)))
            # RETURN: cropped image
            return cropped_image
        # Sleep so it doesn't waste resources
        sleep(.01)

if __name__ == '__main__':
    # Declare Booleans outside of loop
    condition, process = True, True
    # Declare variable for image
    image = None
    while condition:
        # CALL: grab_screen() and store image
        image = grab_screen()
        image.save(r"img\screen_capture.jpg", "JPEG")
