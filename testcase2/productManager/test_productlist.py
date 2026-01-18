import pytest
from common.readyaml import get_testcase_yaml
from conf.OperationConfig import OperationConfig as Env
from common.sendrequests import SendRequests
from common.recordlog import logs
from base.apiutil import BaseRequest
from base.generateId import m_id, t_id
import allure

env = Env()


@allure.feature(next(m_id) + '商品列表')
class TestLogin():

    @allure.story(next(t_id) + '获取商品列表')
    @pytest.mark.smoke
    @pytest.mark.parametrize('baseinfo,params', get_testcase_yaml('./testcase/productManager/getgoodslist.yaml'))
    def test_get_product_list(self, baseinfo, params):
        allure.dynamic.title(params['case_name'])
        BaseRequest().specification_yaml(baseinfo, params)

    @allure.story(next(t_id) + '获取商品详情信息')
    @pytest.mark.smoke
    @pytest.mark.parametrize('baseinfo,params', get_testcase_yaml('./testcase/productManager/productDetail.yaml'))
    def test_get_product_detail(self, baseinfo, params):
        BaseRequest().specification_yaml(baseinfo, params)
