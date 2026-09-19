import pytest
import allure

from common.readyaml import get_testcase_yaml

from base.apiutil import BaseRequest

# 链路顺序：本模块是独立的列表查询用例，不参与状态流转链路，放在链路之后执行（90）
CHAIN_ORDER = 90

# 模块级加载用例数据，按 yaml 中的顺序索引参数化
# 这个 yaml 里有两个 baseInfo 块（带 token / 不带 token），会被展开成两条 [base_info, test_case]
ASN_LIST_CASES = get_testcase_yaml('./testcase/asn/asn_list.yaml')


@allure.feature('入库单(ASN)管理')
class TestAsnList:

    @allure.story('查询入库单列表')
    @pytest.mark.parametrize('case_index', range(len(ASN_LIST_CASES)))
    def test_asn_list(self, case_index):
        base_info, testcase = ASN_LIST_CASES[case_index]
        # 标题加零填充序号前缀：Allure 同 suite 内按标题字母序展示，
        # 加前缀后字母序即等于 yaml 用例顺序，实现按序号排序
        allure.dynamic.title(f"{case_index + 1:02d}-{testcase['case_name']}")
        BaseRequest().specification_yaml(base_info, testcase)
