import pytest
import allure

from common.readyaml import get_testcase_yaml

from base.apiutil import BaseRequest

# 模块级加载用例数据，按 yaml 中的顺序索引参数化
LOGIN_CASES = get_testcase_yaml('./testcase/login/login.yaml')


@allure.feature('登录接口')  # allure报告显示
class TestLogin:

    @allure.story('用户登录校验')
    @pytest.mark.parametrize('case_index', range(len(LOGIN_CASES)))
    def test_login(self, case_index):
        base_info, testcase = LOGIN_CASES[case_index]
        # 标题加零填充序号前缀：Allure 同 suite 内按标题字母序展示，
        # 加前缀后字母序即等于 yaml 用例顺序，实现按序号排序
        allure.dynamic.title(f"{case_index + 1:02d}-{testcase['case_name']}")
        BaseRequest().specification_yaml(base_info, testcase)
