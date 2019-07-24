import os
import re
from time import sleep

from PIL import ImageGrab
from aip import AipOcr
import cv2 as cv
import numpy as np
import win32api
import win32clipboard as wc
import win32con
import win32gui

def grab_im():
    while True:
        cursor_current_x, cursor_current_y = 0, 0
        crop_im = False
        win_DC = win32gui.GetDC(0)
        cursor_origin_x, cursor_origin_y = win32gui.GetCursorPos()
        full_image = ImageGrab.grab(bbox=(0,
                                          0,
                                          win32api.GetSystemMetrics(0),
                                          win32api.GetSystemMetrics(1)))

        while win32api.GetAsyncKeyState(win32con.VK_CONTROL) < 0:
            if not crop_im:
                crop_im = True
            cursor_current_x, cursor_current_y = win32gui.GetCursorPos()
            win32gui.MoveToEx(win_DC, cursor_origin_x, cursor_origin_y)
            win32gui.LineTo(win_DC, cursor_origin_x, cursor_current_y)
            win32gui.MoveToEx(win_DC, cursor_origin_x, cursor_current_y)
            win32gui.LineTo(win_DC, cursor_current_x, cursor_current_y)
            win32gui.MoveToEx(win_DC, cursor_current_x, cursor_current_y)
            win32gui.LineTo(win_DC, cursor_current_x, cursor_origin_y)
            win32gui.MoveToEx(win_DC, cursor_current_x, cursor_origin_y)
            win32gui.LineTo(win_DC, cursor_origin_x, cursor_origin_y)

        if crop_im:
            cropped_image = full_image.crop((min(cursor_current_x,
                                                 cursor_origin_x),
                                             min(cursor_current_y,
                                                 cursor_origin_y),
                                             max(cursor_current_x,
                                                 cursor_origin_x),
                                             max(cursor_current_y,
                                                 cursor_origin_y)))
            return cropped_image
        sleep(.01)

def level_im(tmp_image, rotated_image):
    img = cv.imread(tmp_image)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(
        gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv.warpAffine(
        img, M, (w, h), flags=cv.INTER_CUBIC, borderMode=cv.BORDER_REPLICATE)
    cv.imwrite(rotated_image, rotated)

def ocr(filepath, options):
    with open(filepath, 'rb') as fp:
        return aipOcr.basicAccurate(fp.read(), options)

if __name__ == '__main__':
    ROOT = os.getcwd()
    tmp_image = os.path.join(ROOT, "screen_area.png")
    rotated_image = os.path.join(ROOT, "screen_area_rotated.png")
    image = None
    temp_arr = []
    texts = ""
    pat = re.compile(r'(?<=[^。？！”——……])(\n)')
    APP_ID = '15897536'
    API_KEY = '0AtOpCYua822O6K46QG6830o'
    SECRET_KEY = 'PNPqMHW3wVl6e6gNOGmFpKGFZRgElMtW'
    aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    options = {
        'detect_direction': 'true',
        'language_type': 'CHN_ENG',
    }

    image = grab_im()
    image.save(tmp_image)

    sleep(.01)
    level_im(tmp_image, rotated_image)

    result = ocr(rotated_image, options)

    for i in result['words_result']:
        temp_arr.append(i['words'])
    texts = re.sub(pat, '', '\n'.join(temp_arr))

    wc.OpenClipboard()
    wc.EmptyClipboard()
    wc.SetClipboardData(win32con.CF_UNICODETEXT, texts)
    wc.CloseClipboard()

    os.remove(tmp_image)
    os.remove(rotated_image)
