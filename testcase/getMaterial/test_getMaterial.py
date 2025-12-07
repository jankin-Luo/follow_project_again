import allure
import pytest
import uuid

from common.readyaml import get_testcase_yaml
from base.apiutil import BaseRequest
from base.generateId import m_id, t_id


@allure.feature(next(m_id) + '智慧物流项目')
class Test_aboutMaterial:

    # 场景，allure报告的目录结构
    @allure.story(next(t_id) + "货主托运人下单")
    # 测试用例执行顺序设置
    @pytest.mark.run(order=2)
    # 参数化，yaml数据驱动
    @pytest.mark.parametrize('baseinfo,testcase', get_testcase_yaml("./testcase/getMaterial/xiadan.yaml"))
    def test_xiadan(self, baseinfo, testcase):
        test_id = str(uuid.uuid4())[:8]
        allure.dynamic.title(testcase['case_name'])
        allure.dynamic.parameter("测试ID", testcase['case_name'])
        BaseRequest().specification_yaml(baseinfo, testcase)

    # 场景，allure报告的目录结构
    @allure.story(next(t_id) + "物料下单")
    # 测试用例执行顺序设置
    @pytest.mark.run(order=1)
    # 参数化，yaml数据驱动
    @pytest.mark.parametrize('baseinfo,testcase', get_testcase_yaml("./testcase/getMaterial/getMaterial.yaml"))
    def test_getMaterials(self, baseinfo, testcase):
        test_id = str(uuid.uuid4())[:8]
        allure.dynamic.title(testcase['case_name'])
        allure.dynamic.parameter("测试ID", testcase['case_name'])
        BaseRequest().specification_yaml(baseinfo, testcase)