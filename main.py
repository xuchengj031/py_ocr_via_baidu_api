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
    """
    选择区域截图，返回截取的PIL图片
    """
    while True:
        cursor_current_x, cursor_current_y = 0, 0
        crop_im = False

        # 获取设备环境
        win_DC = win32gui.GetDC(0)
        # 获取鼠标位置
        cursor_origin_x, cursor_origin_y = win32gui.GetCursorPos()
        # 截取全屏
        full_image = ImageGrab.grab(bbox=(0,
                                          0,
                                          win32api.GetSystemMetrics(0),
                                          win32api.GetSystemMetrics(1)))

        # 只有当检测到CTRL键被按下时才进行截
        while win32api.GetAsyncKeyState(win32con.VK_CONTROL) < 0:
            if not crop_im:
                crop_im = True

            # 获取当前鼠标位置
            cursor_current_x, cursor_current_y = win32gui.GetCursorPos()
            # 绘制矩形框
            win32gui.MoveToEx(win_DC, cursor_origin_x, cursor_origin_y)
            win32gui.LineTo(win_DC, cursor_origin_x, cursor_current_y)
            win32gui.MoveToEx(win_DC, cursor_origin_x, cursor_current_y)
            win32gui.LineTo(win_DC, cursor_current_x, cursor_current_y)
            win32gui.MoveToEx(win_DC, cursor_current_x, cursor_current_y)
            win32gui.LineTo(win_DC, cursor_current_x, cursor_origin_y)
            win32gui.MoveToEx(win_DC, cursor_current_x, cursor_origin_y)
            win32gui.LineTo(win_DC, cursor_origin_x, cursor_origin_y)

        # 根据矩形框裁剪
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
    # 读取图像，做二值化处理
    img = cv.imread(tmp_image)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # 像素取反，变成白字黑底
    # gray = cv.bitwise_not(gray)
    ret, thresh = cv.threshold(
        gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    # 计算包含了旋转文本的最小边框
    coords = np.column_stack(np.where(thresh > 0))

    # 该函数给出包含着整个文字区域矩形边框，这个边框的旋转角度和图中文本的旋转角度一致
    angle = cv.minAreaRect(coords)[-1]

    # 调整角度
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # 仿射变换
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv.warpAffine(
        img, M, (w, h), flags=cv.INTER_CUBIC, borderMode=cv.BORDER_REPLICATE)

    cv.imwrite(rotated_image, rotated)


def ocr(filepath, options):
    with open(filepath, 'rb') as fp:
        # 调用通用文字识别接口
        return aipOcr.basicAccurate(fp.read(), options)


if __name__ == '__main__':
    ROOT = os.getcwd()
    tmp_image = os.path.join(ROOT, "screen_area.png")
    rotated_image = os.path.join(ROOT, "screen_area_rotated.png")
    op_text = os.path.join(ROOT, "temp.txt")
    image = None
    temp_arr = []
    texts = ""
    pat = re.compile(r'(?<=[^。？！”——……])(\n)')

    # 百度OCR接口相关设置
    APP_ID = '15897536'
    API_KEY = '0AtOpCYua822O6K46QG6830o'
    SECRET_KEY = 'PNPqMHW3wVl6e6gNOGmFpKGFZRgElMtW'
    aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    # 配置百度OCR识别选项
    options = {
        'detect_direction': 'true',
        'language_type': 'CHN_ENG',
    }

    # 截图
    image = grab_im()
    image.save(tmp_image)

    # 扶正图片
    sleep(.01)
    level_im(tmp_image, rotated_image)

    # 识别内容
    result = ocr(rotated_image, options)

    # 拼接成段落
    for i in result['words_result']:
        temp_arr.append(i['words'])
    texts = re.sub(pat, '', '\n'.join(temp_arr))

    print(texts)

    # 识别结果复制到剪贴板
    wc.OpenClipboard()
    wc.EmptyClipboard()
    wc.SetClipboardData(win32con.CF_UNICODETEXT, texts)
    wc.CloseClipboard()

    # 识别结果保存并打开
    with open(op_text, 'w+', encoding='gbk') as f:
        f.write(texts)
    os.system("notepad {}".format(op_text))
