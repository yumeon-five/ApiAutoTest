import pytest
import allure

from common.readyaml import get_testcase_yaml

from base.apiutil import BaseRequest

# 链路顺序：创建(10) -> 明细(20) -> 预装车(30) -> 预分拣(40) -> 完成分拣(50) -> 查明细(55) -> 上架(60)
CHAIN_ORDER = 60

ASN_MOVETOBIN_CASES = get_testcase_yaml('./testcase/asn/asn_movetobin.yaml')


@allure.feature('入库单(ASN)管理')
class TestAsnMoveToBin:

    @allure.story('ASN商品上架(状态4->5)')
    @pytest.mark.parametrize('case_index', range(len(ASN_MOVETOBIN_CASES)))
    def test_asn_movetobin(self, case_index):
        base_info, testcase = ASN_MOVETOBIN_CASES[case_index]
        allure.dynamic.title(f"{case_index + 1:02d}-{testcase['case_name']}")
        BaseRequest().specification_yaml(base_info, testcase)
