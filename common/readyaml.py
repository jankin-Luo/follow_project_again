import yaml
import os
from conf.setting import FILE_PATH
from common.recordlog import logs

def get_testcase_yaml(file):
    '''
    获取yaml文件的数据
    :param file: 文件路径
    :return:读取到的yaml文件数据
    '''
    try:
        testcase_list = []
        with open(file, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
            if len(yaml_data) <= 1:
                data = yaml_data[0]
                base_info = data.get('baseInfo')
                for ts in data.get('testCase'):
                    param = [base_info,ts]
                    testcase_list.append(param)
                return testcase_list
            else:
                return yaml_data
    except Exception as e:
        print(e)


class ReadYamlData:
    '''
    读取yaml数据，以及写入yaml数据到文件
    '''

    def __init__(self, yaml_file=None):
        if yaml_file is not None:
            self.yaml_file = yaml_file
        else:
            self.yaml_file = '../testcase/login/login.yaml'

    def write_yaml_data(self, value):
        '''
        写入数据到yaml文件
        :param value: dict写入数据
        :return:
        '''
        file_path = FILE_PATH['extract']
        if not os.path.exists(file_path):
            os.system(file_path)

        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                if isinstance(value, dict):
                    write_data = yaml.dump(value, allow_unicode=True, sort_keys=False)
                    f.write(write_data)
                else:
                    logs.error('写入到extact.yaml文件的数据类型必须是字典')
        except Exception as e:
            print(e)

    def get_extract_yaml(self, node_name=None):
        '''
        读取接口提取的变量值
        :param node_name: yaml文件的key值
        :return:
        '''
        if os.path.exists('./extract.yaml'):
            pass
        else:
            print('extract.yaml文件不存在')
            file = open('./extract.yaml', 'w')
            file.close()
            print('extract.yaml文件创建成功')

        with open('./extract.yaml', 'r', encoding='utf-8') as rf:
            extract_data = yaml.safe_load(rf)
            logs.info(f'提取值看下里面几个一样的键:{extract_data}')
            return extract_data[node_name]

    def get_extract_data(self, node_name, sec_node_name = None):
        '''
        获取指定extract.yaml
        :param node_name:
        :param sec_node_name:
        :return:
        '''
        file_path = FILE_PATH['extract']
        if os.path.exists(file_path):
            pass
        else:
            print('extract.yaml不存在')
        try:
            with open(file_path, 'r',encoding='utf-8') as f:
                ext_data = yaml.safe_load(f)
                if sec_node_name is None:
                    return  ext_data[node_name]
                else:
                    return  ext_data[node_name][sec_node_name]
        except Exception as e:
            print(e)

    def clear_yaml_data(self):
        '''清空extract.yaml文件数据'''
        with open(FILE_PATH['extract'],'w') as f:
            f.truncate()

if __name__ == '__main__':
    res = get_testcase_yaml('../testcase/getMaterial/xiadan.yaml')
    print(res)

    '''
    from sendrequests import SendRequests

    send = SendRequests()
    url = 'http://127.0.0.1:8787/dar/user/login'
    data = {
        "user_name": "test01",
        "passwd": "admin123"
    }
    header = None
    method = 'post'
    res = send.run_main(url=url, data=data, header=header, method=method)
    print(res)

    token = res.get('token')
    print(token)

    write_data = {}
    write_data['token'] = token

    read = ReadYamlData()
    # read.write_yaml_data(write_data)
    print(read.get_extract_data('token'))
    # get_testcase_yaml()
    '''
