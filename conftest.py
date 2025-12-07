import pytest,os
from common.recordlog import logs
from common.readyaml import ReadYamlData

read = ReadYamlData()

@pytest.fixture(scope='session',autouse=True)
def clear_extact_data():
    logs.info('------------开始清理extract.yaml------------------')
    read.clear_yaml_data()

@pytest.fixture(scope='class',autouse=True)
def fixture_test(request):
    '''前后置处理'''
    logs.info('-------------这是pytest前后置主要的处理方式--------------')
    yield
    logs.info('------------这是后置处理了---------------')

def pytest_terminal_summary(terminalreporter,exitstatus,config):
    print(terminalreporter.stats)
    case_total = terminalreporter._numcollected
    print(f'测试用例总数:{case_total}')
    failed = len(terminalreporter.stats.get('failed',[]))
    print(f'测试失败总数:{failed}')

# def pytest_configure(config):
#     """配置Allure环境"""
#     # 设置Allure不合并用例
#     os.environ['ALLURE_UNIQUE_NAMES'] = 'true'