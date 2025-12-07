import json

import pytest
from requests import utils
import requests
from common.recordlog import logs
from common.readyaml import ReadYamlData
import allure


class SendRequests():
    '''
    封装接口的请求

    '''

    def __init__(self):
        self.read = ReadYamlData()

    def send_request(self, **kwargs):
        cookie = {}
        session = requests.session()
        res = None
        try:
            res = session.request(**kwargs)
            set_cookie = requests.utils.dict_from_cookiejar(res.cookies)
            if set_cookie:
                cookie['Cookie'] = set_cookie
                self.read.write_yaml_data(cookie)
                logs.info(f'cookie:{cookie}')
            logs.info(f'接口的实际返回信息{res.text.encode("utf-8").decode("unicode_escape") if res.text else res}')
        except requests.exceptions.ConnectionError:
            logs.error('接口连接服务器异常')
            pytest.fail('接口请求异常，可能是requests请求数过多或请求速度过快')
        except requests.exceptions.HTTPError:
            logs.error('HTTP异常')
            pytest.fail('http请求异常')
        except requests.exceptions.RequestException as e:
            logs.error(e)
            pytest.fail('请求异常，数据问题')
        return res

    def run_main(self, name, url, case_name, headers, method, cookies=None, file=None, **kwargs):
        '''
        封装请求主函数
        :param url: 连接
        :param data: 请求数据
        :param header: 请求头
        :param method: 请求方法
        :return:
        '''
        # 收集报告日志信息
        try:
            logs.info(f'接口名称：{name}')
            logs.info(f'接口请求地址：{url}')
            logs.info(f'请求方法：{method}')
            logs.info(f'测试用例名称：{case_name}')
            logs.info(f'请求头：{headers}')
            logs.info(f'Cookies：{cookies}')
            req_params = json.dumps(kwargs, ensure_ascii=False)
            if 'data' in kwargs.keys():
                logs.info(f'请求参数:{kwargs}')
                allure.attach(req_params,f'请求参数：{req_params}',allure.attachment_type.TEXT)
            elif 'json' in kwargs.keys():
                logs.info(f'请求参数:{kwargs}')
                allure.attach(req_params, f'请求参数：{req_params}', allure.attachment_type.TEXT)
            elif 'params' in kwargs.keys():
                logs.info(f'请求参数:{kwargs}')
                allure.attach(req_params, f'请求参数：{req_params}', allure.attachment_type.TEXT)
        except Exception as e:
            logs.error(e)

        res = self.send_request(method=method, url=url, headers=headers, cookies=cookies, files=file, verify=False,
                                **kwargs)

        return res


if __name__ == '__main__':
    url = 'http://127.0.0.1:8787/dar/user/login'
    data = {
        "user_name": "test01",
        "passwd": "admin123"
    }
    header = None
    method = 'post'

    send = SendRequests()
    res = send.send_request(url=url, data=data, method=method)
    print(res)
