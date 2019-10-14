#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: yinhaozheng
@software: PyCharm
@file: app.py
@time: 2019-10-14 17:23
"""

__mtime__ = '2019-10-14'

import os
from flask import Flask, request
from flask_uploads import UploadSet, configure_uploads, IMAGES, \
    patch_request_class

import subprocess
from shutil import copyfile

app = Flask(__name__)
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()  # 文件储存地址

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # 文件大小限制，默认为16MB

cwd = "/home/bayesai/yinhaozheng/Face-Liveness_detection/"
shell = "./dlib_test_process"
face_path = os.path.join(cwd, "face")

ir_target = os.path.join(face_path, "0000_IR_frontface.jpg")
raw_target = os.path.join(face_path, "raw_0000_frontface.raw")

html = '''
    <!DOCTYPE html>
    <title>Upload File</title>
    <h1>图片上传</h1>
    <form method=post enctype=multipart/form-data>
         <input  type=file name=ir>    <p>ir</p>
         <input  type=file name=raw>   <p>raw</p>
         <input  type=file name=depth> <p>depth</p>
         <input type=submit value=上传>
    </form>
    '''


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print(request.files)
        ir = photos.save(request.files['ir'])
        raw = photos.save(request.files['raw'])
        # depth = photos.save(request.files['depth'])
        file_url = photos.url(ir)

        ir_source, raw_source = photos.path(ir), photos.path(raw)
        clean()
        copyfile(ir_source, ir_target)
        copyfile(raw_source, raw_target)

        sub = subprocess.Popen(shell, shell=True, cwd=cwd, stdout=subprocess.PIPE)
        sub.wait()
        b = sub.stdout.read()
        text = str(b, encoding="utf-8")
        result = text.split("\n")
        return html + '<h1>' + result[14] + '</h1>' + '<br><img src=' + file_url + '>'
    return html


def clean():
    if os.path.exists(ir_target):
        os.remove(ir_target)
    if os.path.exists(raw_target):
        os.remove(raw_target)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
