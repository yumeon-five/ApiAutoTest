import pytest
import allure

from common.readyaml import get_testcase_yaml

from base.apiutil import BaseRequest

# 链路顺序：登录(0) -> 供应商(2)/商品(3)/库位(4)/库存基线(5) -> 创建(10) -> 明细(20) -> 预装车(30)
#           -> 预分拣(40) -> 完成分拣(50) -> 查明细(55) -> 上架(60) -> 总库存核对(70)/库位库存(71)/按ID查主单(72)
CHAIN_ORDER = 71

ASN_BIN_STOCK_QUERY_CASES = get_testcase_yaml('./testcase/asn/asn_bin_stock_query.yaml')


@allure.feature('入库单(ASN)管理')
class TestBinStockQuery:

    @allure.story('查询库位库存')
    @pytest.mark.parametrize('case_index', range(len(ASN_BIN_STOCK_QUERY_CASES)))
    def test_bin_stock_query(self, case_index):
        base_info, testcase = ASN_BIN_STOCK_QUERY_CASES[case_index]
        allure.dynamic.title(f"{case_index + 1:02d}-{testcase['case_name']}")
        BaseRequest().specification_yaml(base_info, testcase)
