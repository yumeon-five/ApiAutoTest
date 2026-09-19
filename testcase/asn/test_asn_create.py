import pytest
import allure

from common.readyaml import get_testcase_yaml

from base.apiutil import BaseRequest

# 模块级加载用例数据，按 yaml 中的顺序索引参数化。
# 这个 yaml 有两个 baseInfo 块（先 POST 创建、再 GET 按 asn_code 回查），
# 展开后是 4 条用例，顺序与 yaml 一致 —— 接口关联（创建 -> 提取 asn_code -> 回查）依赖这个顺序
ASN_CREATE_CASES = get_testcase_yaml('./testcase/asn/asn_create.yaml')


@allure.feature('入库单(ASN)管理')
class TestAsnCreate:

    @allure.story('创建入库单主单')
    @pytest.mark.parametrize('case_index', range(len(ASN_CREATE_CASES)))
    def test_asn_create(self, case_index):
        base_info, testcase = ASN_CREATE_CASES[case_index]
        # 标题加零填充序号前缀：Allure 同 suite 内按标题字母序展示，
        # 加前缀后字母序即等于 yaml 用例顺序，实现按序号排序
        allure.dynamic.title(f"{case_index + 1:02d}-{testcase['case_name']}")
        BaseRequest().specification_yaml(base_info, testcase)
