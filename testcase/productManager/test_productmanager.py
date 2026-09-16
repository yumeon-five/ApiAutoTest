import pytest
import allure

from common.readyaml import get_testcase_yaml

from base.apiutil import BaseRequest

@allure.feature('商品管理') #allure报告显示
class TestProductManager(object):

    @allure.story('获取商品列表接口')
    @pytest.mark.parametrize('params',get_testcase_yaml('./testcase/productManager/getProductList.yaml'))
    def test_get_productlist(self, params):
        BaseRequest().specification_yaml(params)

    @allure.story('获取商品详情')
    @pytest.mark.parametrize('params',get_testcase_yaml('./testcase/productManager/productdetail.yaml'))
    def test_get_productdetail(self, params):
        BaseRequest().specification_yaml(params)