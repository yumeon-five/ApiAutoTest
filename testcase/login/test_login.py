import pytest
import allure

from common.readyaml import get_testcase_yaml

from base.apiutil import BaseRequest

# 链路顺序：登录(0) -> 创建(10) -> 明细(20) -> 预装车(30) -> 预分拣(40) -> 完成分拣(50) -> 查明细(55) -> 上架(60)
# 由 conftest.py 的 pytest_collection_modifyitems 读取
CHAIN_ORDER = 0

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
