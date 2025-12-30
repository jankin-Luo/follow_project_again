import operator
import os.path
import allure
import jsonpath

from common.recordlog import logs
from common.connection import ConnectMysql


class Assertions:
    '''
    断言接口模式，支持：
    1、字符串
    2、结果相等断言
    3、结果不相等断言
    4、断言接口返回值里面的任意一个值
    5、数据库断言
    '''

    def _log_and_attach(self, error_type, error_msg, attachment_title):
        '''统一日志和allure处理报告'''
        logs.error(f'{error_type}: {error_msg}')
        allure.attach(f'错误类型:{error_type}\n错误信息: {error_msg}',
                      attachment_title,
                      attachment_type=allure.attachment_type.TEXT)

    def contains_assert(self, value, response, status_code):
        '''
        第一种模式，字符串包含断言，断言预期结果字符串包含在接口返回中
        :param value:
        :param response:
        :param status_code:
        :return:
        '''
        # 断言状态表示，0代表成功，其他代表失败
        flag = 0
        for assert_k, assert_v in value.items():
            # print(assert_k, assert_v)
            if assert_k == 'status_code':
                if assert_v != status_code:
                    flag += 1
                    #优化版
                    error_type = '技术问题'
                    error_msg = f'状态码不正确，预期为{assert_v},实际为{status_code}'
                    self._log_and_attach(error_type, error_msg, f'状态码断言失败')
                    # allure.attach(f'预期结果:{assert_v}\n实际结果:{status_code}', '响应代码断言结果:失败',
                    #               allure.attachment_type.TEXT)
                    # logs.error('contains断言失败，接口返回码{}不等于预期{}'.format(status_code, assert_v))
                else:
                    logs.info(f'状态码匹配{status_code}={assert_v}')
            else:
                res_list = jsonpath.jsonpath(response, '$..%s' % assert_k)
                if isinstance(res_list[0], str):
                    res_list = ''.join(res_list)
                if res_list:
                    if assert_v in res_list:
                        logs.info(f'字符串包含，断言成功：预期结果：{assert_v}\n,实际结果:{res_list}')
                    else:
                        flag += 1
                        logs.error(f'预期结果：{assert_v}\n,实际结果:{res_list}，响应文本断言结果:失败')
                        allure.attach(f'预期结果:{assert_v}\n实际结果:{res_list}', '响应文本断言结果:失败',
                                      allure.attachment_type.TEXT)
        return flag

    def equal_assert(self, value, response):
        '''
        相等断言模式
        :param value:预期结果，也就是yaml文件中的validation中的关键字参数，必须为dict类型
        :param response:接口的实际返回结果
        :return:flag标识，0为通过，其他为不通过
        '''
        flag = 0
        res_list = []
        if isinstance(value, dict) and isinstance(response, dict):
            # 处理实际结果的数据结构，保持与预期结果一致
            for i in response:
                if list(value.keys())[0] != i:
                    res_list.append(i)
            print(res_list)
            for i in res_list:
                del (response[i])

            # 通过判断实际结果与预期结果的字典是否一致
            eq_assert = operator.eq(response, value)
            if eq_assert:
                logs.info(f'相等断言成功，接口实际结果为{response}，等于预期结果{value}')
            else:
                flag += 1
                logs.error(f'相等断言失败，接口实际结果为{response}，不等于预期结果{value}')
        else:
            raise TypeError('断言失败，类型错误，预期结果和接口返回数据类型均需要字典类型！')
        return flag

    def not_equal_assert(self, value, response):
        '''
        不相等断言模式
        :param value:预期结果，也就是yaml文件中的validation中的关键字参数，必须为dict类型
        :param response:接口的实际返回结果
        :return:flag标识，0为通过，其他为不通过
        '''
        flag = 0
        res_list = []
        if isinstance(value, dict) and isinstance(response, dict):
            # 处理实际结果的数据结构，保持与预期结果一致
            for i in response:
                if list(value.keys())[0] != i:
                    res_list.append(i)
            print(res_list)
            for i in res_list:
                del (response[i])

            # 通过判断实际结果与预期结果的字典是否一致
            eq_assert = operator.ne(response, value)
            if eq_assert:
                logs.info(f'相等断言成功，接口实际结果为{response}，不等于预期结果{value}')
            else:
                flag += 1
                logs.error(f'不相等断言失败，接口实际结果为{response}，等于预期结果{value}')
        else:
            raise TypeError('断言失败，类型错误，预期结果和接口返回数据类型均需要字典类型！')
        return flag

    def assert_mysql(self, expected_sql):
        '''数据库断言'''
        flag = 0
        conn = ConnectMysql()
        db_value = conn.query(expected_sql)
        if db_value is not None:
            logs.info('数据库断言成功')
            return flag
        else:
            logs.error('数据库断言失败，数据库中不存在该数据')
            flag += 1
            return flag

    def assert_result(self, expected, response, status_code):
        '''
        断言模式，通过all_flag标记
        :param expoected:预期结果
        :param response:接口实际返回结果
        :param status_code:接口实际返回状态码
        :return:
        '''
        # 0代表成功
        all_flag = 0
        try:
            for yq in expected:
                for k, v in yq.items():
                    if k == 'contains':
                        flag = self.contains_assert(v, response, status_code)
                        all_flag += flag
                    elif k == 'eq':
                        flag = self.equal_assert(v, response)
                        all_flag += flag
                    elif k == 'ne':
                        flag = self.not_equal_assert(v, response)
                        all_flag += flag
                    elif k == 'db':
                        flag = self.assert_mysql(v)
                        all_flag += flag
            assert all_flag == 0
            logs.info('测试成功')
        except Exception as e:
            logs.error('测试失败')
            logs.error(f'异常信息{e}')
            assert False


if __name__ == '__main__':
    from common.readyaml import get_testcase_yaml

    data = get_testcase_yaml(os.path.join(os.path.dirname(__file__), '../testcase/Login', 'login.yaml'))[0]
    value = data['testCase'][0]['validation']
    response = {
        "error_code": None,
        "msg": "登录成功",
        "msg_code": 200,
        "orgId": "4140913758110176843",
        "token": "2fbBCd57fABA3Af8deF3D8daa42Eb",
        "userId": "4099567845459245623"
    }

    # print(response.keys())
    # for i in response:
    #     print(i)
    ass = Assertions()
    for i in value:
        for k, v in i.items():
            ass.assert_mysql(v)
