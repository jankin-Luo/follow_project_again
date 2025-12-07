# 用于操作yaml文件数据中的动态变量的模块，到目前第8课为止，用于读取从接口中得到并存储在extract.yaml中的信息
import datetime
import random

from common.readyaml import ReadYamlData


class DebugTalk:

    def __init__(self):
        self.read = ReadYamlData()

    def get_extract_order_data(self, data, randoms):
        if randoms not in [0, -1, -2]:
            return data[randoms - 1]

    def get_extract_data_list(self, node_name, randoms=None):
        '''
        获取extract.yaml的数据
        :param node_name: extract.yaml中的key值
        :param random: 随机读取extract.yaml中的数据
        :return:
        '''
        data = self.read.get_extract_data(node_name)
        if randoms is not None:
            randoms = int(randoms)
            data_value = {
                randoms: self.get_extract_order_data(data, randoms),
                0: random.choice(data),
                -1: ','.join(data),
                -2: data
            }
            data = data_value[randoms]
        return data

    def get_extract_data(self, node_name, sec_node_name=None):
        '''
        获取extract.yaml的数据
        :param node_name: extract.yaml中的key值
        :param random: 随机读取extract.yaml中的数据
        :return:
        '''
        data = self.read.get_extract_data(node_name, sec_node_name)
        return data

    def get_now_date(self):
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return now_time

    def md5_params(self, params):
        # print('实现md5加密')
        return 'adagasds' + params


if __name__ == '__main__':
    debug = DebugTalk()
    data = debug.get_extract_data('Cookie')
    print(data)
    # print(debug.get_now_date())
