import pytest
import allure

from common.readyaml import get_testcase_yaml

from base.apiutil import BaseRequest

# 链路顺序：创建(10) -> 明细(20) -> 预装车(30) -> 预分拣(40) -> 完成分拣(50) -> 查明细(55) -> 上架(60)
# 由 conftest.py 的 pytest_collection_modifyitems 读取，文件名排序不等于业务顺序
CHAIN_ORDER = 30

ASN_PRELOAD_CASES = get_testcase_yaml('./testcase/asn/asn_preload.yaml')


@allure.feature('入库单(ASN)管理')
class TestAsnPreLoad:

    @allure.story('ASN预装车(状态1->2)')
    @pytest.mark.parametrize('case_index', range(len(ASN_PRELOAD_CASES)))
    def test_asn_preload(self, case_index):
        base_info, testcase = ASN_PRELOAD_CASES[case_index]
        allure.dynamic.title(f"{case_index + 1:02d}-{testcase['case_name']}")
        BaseRequest().specification_yaml(base_info, testcase)
