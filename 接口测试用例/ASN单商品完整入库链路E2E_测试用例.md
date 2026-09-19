---
interface_key: asnE2EFlow
interface_name: ASN单商品完整入库链路E2E
---

## ASN单商品完整入库链路E2E - 端到端串联登录到上架全流程

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | ca1f7366a463478ab508a985ccd15de4 |
| 测试标题 | ASN单商品完整入库链路-端到端串联登录到上架全流程 |
| 前置条件 | 系统存在有效账号 {{ 正确账号 }} / 密码 {{ 正确密码 }}；存在可用供应商、可用商品、Normal 类型空库位；测试数据库已恢复基线；使用独立 fixture 准备数据不依赖其他用例执行顺序 |
| 优先级 | P0 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/login/ → /supplier/ → /goods/ → /binset/ → /stock/list/ → /asn/list/ → /asn/detail/ → /asn/detail/ → /asn/preload/{{ ASN主键ID }}/ → /asn/presort/{{ ASN主键ID }}/ → /asn/sorted/{{ ASN主键ID }}/ → /asn/movetobin/{{ ASN明细ID }}/ → /stock/list/ → /stock/bin/ |
| 请求方法 | POST + GET |

### 请求头

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| Content-Type | application/json | JSON 请求体 |
| Accept | application/json | 期望 JSON 响应 |
| token | {{ 有效Token }} | 登录返回的 openid，链路中提取后携带 |
| operator | {{ 操作员ID }} | 登录返回的 user_id，链路中提取后携带 |

### URL参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| page | {{ 当前页码 }} | 各查询接口按需携带 |
| max_page | {{ 分页大小 }} | 各查询接口按需携带 |
| format | json | 各接口响应格式 |
| asn_code | {{ ASN编号 }} | 明细查询与筛选接口按需携带 |
| goods_code | {{ 商品编码 }} | 库存查询接口按需携带 |
| bin_name | {{ 库位名称 }} | 库位库存查询接口按需携带 |
| bin_property | Normal | 库位查询接口按需携带 |
| empty_label | true | 库位查询接口按需携带 |
| asn_id | {{ ASN主键ID }} | 状态流转接口路径参数 |
| detail_id | {{ ASN明细ID }} | 上架接口路径参数 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| ordered_qty | {{ 计划数量 }} | 计划到货数量（示例 10） |
| actual_qty | {{ 实到数量 }} | 实际到货数量（示例 10） |
| putaway_qty | {{ 上架数量 }} | 上架数量（示例 10） |
| run_id | {{ 运行标识 }} | 唯一测试运行标识，保证测试数据可追踪 |

### 预期结果

- 所有子接口 HTTP 状态码均为 200
- 关联变量在链路中正确传递（token、operator、supplier_name、goods_code、bin_name、asn_id、asn_code、detail_id）
- ASN 主单与明细状态严格按 1→2→3→4→5 顺序流转
- 最终 asn_status=5、detail_status=5、goods_qty={{ 计划数量 }}、goods_actual_qty={{ 实到数量 }}、sorted_qty={{ 上架数量 }}
- 数据库 stocklist 表 goods_qty、onhand_stock、can_order_stock 均比基线增加 {{ 上架数量 }}
- 数据库 stocklist 表中间阶段库存 asn_stock、pre_load_stock、pre_sort_stock、sorted_stock 均回到基线（增量为 0）
- 数据库 stockbin 表对应库位商品数量合计增加 {{ 上架数量 }}
- 所有接口返回值与数据库最终状态一致
- Allure 报告中本用例只统计为 1 条
