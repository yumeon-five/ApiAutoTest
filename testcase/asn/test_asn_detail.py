import pytest
import allure

from common.readyaml import get_testcase_yaml

from base.apiutil import BaseRequest

# 模块级加载用例数据，按 yaml 中的顺序索引参数化
# 依赖 testcase/asn/test_asn_create.py 先执行（它把 asn_code 提取到 extract.yaml）
ASN_DETAIL_CASES = get_testcase_yaml('./testcase/asn/asn_detail.yaml')


@allure.feature('入库单(ASN)管理')
class TestAsnDetail:

    @allure.story('添加ASN商品明细')
    @pytest.mark.parametrize('case_index', range(len(ASN_DETAIL_CASES)))
    def test_asn_detail(self, case_index):
        base_info, testcase = ASN_DETAIL_CASES[case_index]
        # 标题加零填充序号前缀：Allure 同 suite 内按标题字母序展示，
        # 加前缀后字母序即等于 yaml 用例顺序，实现按序号排序
        allure.dynamic.title(f"{case_index + 1:02d}-{testcase['case_name']}")
        BaseRequest().specification_yaml(base_info, testcase)
