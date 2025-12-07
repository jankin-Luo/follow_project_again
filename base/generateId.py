def genetate_module_id():
    '''
    生成测试模块编号，保障allure报告的顺序与pytest设置的执行顺序保持一致
    :return:
    '''
    for i in range(1, 1000):
        module_id = 'M' + str(i).zfill(2) + '_'
        yield module_id


def generate_testcase_id():
    '''
    生成测试用例id
    :return:
    '''
    for i in range(1, 10000):
        testcase_id = 'T' + str(i).zfill(3) + '_'
        yield testcase_id

m_id = genetate_module_id()
t_id = generate_testcase_id()
