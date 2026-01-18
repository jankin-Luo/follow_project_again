import allure
import pytest
import uuid

from common.readyaml import get_testcase_yaml
from base.apiutil import BaseRequest
from base.generateId import m_id, t_id


@allure.feature(next(m_id) + '若以项目')
class Test_aboutMaterial:

    # 场景，allure报告的目录结构
    @allure.story(next(t_id) + "登陆接口")
    # 测试用例执行顺序设置
    @pytest.mark.run(order=2)
    # 参数化，yaml数据驱动
    @pytest.mark.parametrize('baseinfo,testcase', get_testcase_yaml("./testcase/ruoyitest/login.yaml"),ids=[1,2,3,4,5])
    def test_xiadan(self, baseinfo, testcase):
        test_id = str(uuid.uuid4())[:8]
        # allure.dynamic.title(testcase['case_name'])
        allure.dynamic.parameter("测试ID", testcase['case_name'])
        BaseRequest().specification_yaml(baseinfo, testcase)

