# coding=utf-8

import sys
import json
import base64
import os

# 保证兼容python2以及python3
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib2
    from urllib import quote_plus
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode

# 防止https证书校验不正确
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# 百度AI识别图片文字服务KEY
API_KEY = 'mVQbGIdgIF04Kgcj8NR95GjH'
SECRET_KEY = 'VheQqSG083AqfZQReqV39Xdx5TWeGmiI'

OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'

"""
    获取token
"""
def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    if (IS_PY3):
        result_str = result_str.decode()


    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print ('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()

"""
    读取文件
"""
def read_file(image_path):
    f = None
    try:
        f = open(image_path, 'rb')
        return f.read()
    except:
        print('read image file fail')
        return None
    finally:
        if f:
            f.close()


"""
    调用远程服务
"""
def request(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        if (IS_PY3):
            result_str = result_str.decode()
        return result_str
    except  URLError as err:
        print(err)
        
#遍历文件夹获取所有文件
def get_files_name(images_dir = "images",files_dir = "images"):
    images_path = []
    files_path = []
    for filename in os.listdir(images_dir):
        if filename.endswith(('.png','.jpg','.bmp','.jpeg')):
            images_path.append(os.path.join(images_dir, filename))
            if filename.endswith("jpeg"):
                files_path.append(os.path.join(files_dir, filename[:-4] + "txt"))
            else:
                files_path.append(os.path.join(files_dir, filename[:-3] + "txt"))
    return images_path,files_path
    
    
def basic_save_txt(text,filename):
    fw = open(filename, "a+", encoding="utf-8")
    fw.write(text)
    fw.close()

if __name__ == '__main__':

    # 获取access token
    token = fetch_token()
    # 拼接图像审核url
    image_url = OCR_URL + "?access_token=" + token

    images_path,files_path = get_files_name()

    for i,item in enumerate(images_path):
        image_path = images_path[i]
        file_path = files_path[i]
        
        print("开始识别:" + image_path)
        
        text = ""
        file_content = read_file(image_path)
        result = request(image_url, urlencode({'image': base64.b64encode(file_content)}))
        result_json = json.loads(result)
        for words_result in result_json["words_result"]:
            text = text + "\n" + words_result["words"]
        
        basic_save_txt(text, file_path)
        print("导出完毕:" + file_path)


    



