import pytest
import allure

from common.readyaml import get_testcase_yaml

from base.apiutil import BaseRequest

@allure.feature('登录接口') #allure报告显示
class TestLogin:

    @allure.story('用户名和密码正常校验')
    @pytest.mark.parametrize('base_info,testcase',get_testcase_yaml('./testcase/login/login.yaml'))
    def test_case01(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        BaseRequest().specification_yaml(base_info, testcase)
