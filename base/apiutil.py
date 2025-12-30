# 解析yaml文件里接口数据中的动态变量函数
import json
import re

import jsonpath as jsonpath

from common.recordlog import logs
from common.readyaml import ReadYamlData, get_testcase_yaml
from common.debugtalk import DebugTalk
from conf.OperationConfig import OperationConfig
from common.sendrequests import SendRequests
import allure
from common.assertions import Assertions

assert_res = Assertions()


class BaseRequest:

    def __init__(self):
        self.read = ReadYamlData()
        self.conf = OperationConfig()
        self.send = SendRequests()

    def replace_load(self, data):
        '''yaml文件替换解析${}格式的数据'''

        str_data = data
        if not isinstance(data, str):
            str_data = json.dumps(data, ensure_ascii=False)
            # logs.info(str_data)

        # print(str_data.count('${'))
        for i in range(str_data.count('${')):
            if '${' in str_data and '}' in str_data:
                # index检测字符串是否
                start_index = str_data.index('$')
                end_index = str_data.index('}', start_index)
                ref_all_params = str_data[start_index:end_index + 1]
                # 取出函数名
                func_name = ref_all_params[2:ref_all_params.index('(')]
                # 取出函数里面的参数值
                funcs_params = ref_all_params[ref_all_params.index('(') + 1:ref_all_params.index(')')]
                # 传入替换的参数获取对应值
                extract_data = getattr(DebugTalk(), func_name)(*funcs_params.split(',') if funcs_params else "")
                str_data = str_data.replace(ref_all_params, str(extract_data))
                # print(str_data)

        #这里这个判断不是很懂,原本传参是data，我改成了extract_data,好想不对。(已解决1、项目中cookie要求值为字典；参数中存在要求值为字符的
        # 情况，但视频中只处理了参数中可能存在值为字典的情况，cookie传的字典被处理成了字符串。2、json.loads处理单括号字符串为字典报错，改用
        # eval()处理，eval说有很多隐患，暂未深究。)
        if data :
            if isinstance(data, dict) or isinstance(extract_data,dict):
                # data = json.loads(str_data)
                data = eval(str_data)
        else:
            data = str_data

        return data

    # 将结构化的yaml接口、用例数据封装成通用的方法，运行该方法可以读取yaml中的接口信息直接请求接口，读取用例信息执行测试业务并断言。
    def specification_yaml(self, baseinfo,case_info):
        '''
        规范yaml接口测试数据的写法
        :param case_info: list，调取case_info[0]
        :return:
        '''
        cookies = None
        params_type = ['params', 'data', 'json']
        # print(case_info)
        try:
            base_url = self.conf.get_env('host')
            url = base_url + baseinfo['url']
            allure.attach(url, f'接口地址:{url}')
            api_name = baseinfo['api_name']
            allure.attach(api_name, f'接口名称:{api_name}')
            method = baseinfo['method']
            allure.attach(method, f'请求方法:{method}')
            header = baseinfo['header']
            allure.attach(str(header), f'请求头:{header}', allure.attachment_type.TEXT)
            try:
                cookies = self.replace_load(baseinfo['cookies'])
                logs.info(cookies)
                allure.attach(cookies, f'cookies:{cookies}', allure.attachment_type.TEXT)
            except:
                pass

            tc =case_info
            case_name = tc.pop('case_name')
            allure.attach(case_name, f'测试用例名称:{case_name}')
            validation = tc.pop('validation')
            extract = tc.pop('extract', None)
            extract_list = tc.pop('extract_list', None)
            for k, v in tc.items():
                if k in params_type:
                    tc[k] = self.replace_load(v)
            #处理上传接口
            file, files = tc.pop('files', None), None
            if file is not None:
                for fk, fv in file.items():
                    allure.attach(json.dumps(file), '导入文件')
                    files = {fk: open(fv, mode='rb')}
            # with allure.step('请求接口地址'):
            res = self.send.run_main(name=api_name, case_name=case_name, url=url, headers=header, method=method,
                                     cookies=cookies, file=files, **tc)
            res_text = res.text
            # logs.info(f'text区别是啥：{json.loads(res_text)}')
            # logs.info(f'json区别是啥：{res.json()}')
            allure.attach(res.text.encode('utf-8').decode('unicode_escape'), f'接口响应信息', allure.attachment_type.TEXT)
            allure.attach(str(res.status_code), f'接口响应码', allure.attachment_type.TEXT)

            res_json = res.json()
            if extract is not None:
                self.extract_data(extract, res_text)
            if extract_list is not None:
                self.extract_data_list(extract_list, res.text)
            # 处理接口断言
            assert_res.assert_result(validation, res_json, res.status_code)
        except Exception as e:
            logs.error(e)
            raise e

    def extract_data(self, testcase_extract, response):
        '''
        提取接口返回值,支持正则表达式提取，以及json提取
        :param testcase_extract: yaml文件中的extract的值
        :param response: 接口的实际返回值
        :return:
        '''
        pattern_list = ['(.+?)', '(.*?)', r'(\d+)', r'(\d*)']
        try:
            for k, v in testcase_extract.items():
                # 处理正则表达式处理
                for pat in pattern_list:
                    if pat in v:
                        ext_list = re.search(v, response)
                        if pat in [r'(\d+)', r'(\d*)']:
                            extract_data = {k: int(ext_list.group(1))}
                        else:
                            extract_data = {k: ext_list.group(1)}
                        logs.info(f'正则表达式提取到的参数:{extract_data}')
                        self.read.write_yaml_data(extract_data)
                if '$' in v:
                    ext_json = jsonpath.jsonpath(json.loads(response), v)[0]
                    if ext_json:
                        extract_data = {k: ext_json}
                    else:
                        extract_data = {k: '未提取到数据，要么接口返回空，要么表达式问题'}
                    logs.info(f'json提取到的{extract_data}')
                    self.read.write_yaml_data(extract_data)
        except:
            logs.error('接口返回值提取异常，请检查yaml的extract表达式对不对')

    def extract_data_list(self, testcase_extract, response):
        '''
        提取接口返回值,支持正则表达式提取，以及json提取
        :param testcase_extract: yaml文件中的extract的值
        :param response: 接口的实际返回值
        :return:
        '''
        try:
            for k, v in testcase_extract.items():
                if '$' in v:
                    # logs.info(f'传入的响应信息是：{response}')
                    ext_json = jsonpath.jsonpath(json.loads(response), v)
                    if ext_json:
                        extract_data = {k: ext_json}
                    else:
                        extract_data = {k: '未提取到数据，要么接口返回空，要么表达式问题'}
                    logs.info(f'json提取到的{extract_data}')
                    self.read.write_yaml_data(extract_data)
        except:
            logs.error('接口返回值提取异常，请检查yaml的extract表达式对不对')


if __name__ == '__main__':
    data = get_testcase_yaml('../testcase/getMaterial/xiadan.yaml')
    # data = get_testcase_yaml('../testcase/login/login.yaml')
    # print(data[0])
    # print(data[0][0])
    # print(data[0][1])
    req = BaseRequest()
    # print(data[0][0]['cookies'])
    res = req.specification_yaml(data[0][0],data[0][1])
