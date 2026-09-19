import pytest
import allure

from common.readyaml import get_testcase_yaml

from base.apiutil import BaseRequest

# 链路顺序：创建(10) -> 明细(20) -> 预装车(30) -> 预分拣(40) -> 完成分拣(50) -> 查明细(55) -> 上架(60)
CHAIN_ORDER = 55

ASN_DETAIL_QUERY_CASES = get_testcase_yaml('./testcase/asn/asn_detail_query.yaml')


@allure.feature('入库单(ASN)管理')
class TestAsnDetailQuery:

    @allure.story('按ASN编号查询商品明细')
    @pytest.mark.parametrize('case_index', range(len(ASN_DETAIL_QUERY_CASES)))
    def test_asn_detail_query(self, case_index):
        base_info, testcase = ASN_DETAIL_QUERY_CASES[case_index]
        allure.dynamic.title(f"{case_index + 1:02d}-{testcase['case_name']}")
        BaseRequest().specification_yaml(base_info, testcase)
