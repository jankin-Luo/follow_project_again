# import pytest
# from execnet.script.quitserver import hostport
from curses import wrapper


# def teardown_method():
#     print('结束测试')
#
# def test_main():
#     print('开始测试')
#     assert 1==1
#
# def setup_method():
#     print('初始化测试')
#
from flask import Flask
import time,flask

app = Flask(__name__)


@app.route('/test', methods=['POST'])
def test():
    user =  flask.request.form.get('username')
    if user == 'admin':
        return flask.jsonify({'msg':'登录成功'})
    else:
        return flask.jsonify({'msg':'登录失败'})


import threading

t = threading.Thread(target=app.run, args=['127.0.0.1', '5001'], daemon = True)
t.start()
time.sleep(1)
import requests

a = requests.post(url="http://127.0.0.1:5001/test",data={'username':'admin'})
print(a.text.encode('utf-8').decode('unicode_escape'))

