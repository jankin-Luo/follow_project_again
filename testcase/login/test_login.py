import pytest
from common.readyaml import get_testcase_yaml
from conf.OperationConfig import OperationConfig as Env
from common.sendrequests import SendRequests
from common.recordlog import logs
from base.apiutil import BaseRequest
from base.generateId import m_id, t_id
import allure

env = Env()


@allure.feature(next(m_id) + '登录接口')
class TestLogin():

    @pytest.mark.run(order=0)
    @allure.story(next(t_id) + '用户名和密码正常校验')
    @pytest.mark.smoke
    @pytest.mark.parametrize('baseinfo,params', get_testcase_yaml('./testcase/login/login.yaml'))
    def test_case04(self, baseinfo, params):
        BaseRequest().specification_yaml(baseinfo, params)
