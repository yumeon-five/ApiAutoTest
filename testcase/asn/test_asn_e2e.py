import allure

from common.readyaml import get_testcase_yaml

from base.apiutil import BaseRequest

# 链路顺序：放在分步链路之后（分步链路到 72，独立查询用例在 90）
CHAIN_ORDER = 80

# 整条链路的所有步骤，顺序与 yaml 一致
E2E_STEPS = get_testcase_yaml('./testcase/asn/asn_e2e.yaml')


@allure.feature('入库单(ASN)管理')
class TestAsnE2E:
    """
    ASN 单商品完整入库链路 E2E。

    和分步链路模块（test_asn_create / test_asn_detail / ...）的区别：
    - 分步链路按接口拆成多条用例、靠 CHAIN_ORDER 串起来，失败能定位到具体哪一步（回归用）
    - 本用例把整条链路压成 1 条：自带登录、不依赖其他模块的执行顺序，
      Allure 报告里只统计 1 条（用例文档 ASN单商品完整入库链路E2E 的要求）
    """

    @allure.story('ASN单商品完整入库链路E2E')
    @allure.title('01-登录到上架全流程端到端')
    def test_asn_e2e(self):
        # 一个测试函数里连续发十几个请求，每步用 allure.step 包起来：
        # 报告里只算 1 条用例，但点开能看到每一步的请求参数、响应和断言附件
        for index, (base_info, testcase) in enumerate(E2E_STEPS, start=1):
            with allure.step(f"{index:02d}-{base_info['api_name']}：{testcase['case_name']}"):
                BaseRequest().specification_yaml(base_info, testcase)
