from aip import AipOcr
import os

# 下面3个变量请自行更改
APP_ID = '15897536'
API_KEY = '0AtOpCYua822O6K46QG6830o'
SECRET_KEY = 'PNPqMHW3wVl6e6gNOGmFpKGFZRgElMtW'
ROOT = os.getcwd()
aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)

# 读取图片
filePath = os.path.join(ROOT, "img", "test0.png")


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

# 定义参数变量
options = {
    'detect_direction': 'true',
    'language_type': 'CHN_ENG',
}

# 调用通用文字识别接口
result = aipOcr.basicAccurate(get_file_content(filePath), options)

print(result)
