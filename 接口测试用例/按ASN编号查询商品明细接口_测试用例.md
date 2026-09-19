---
interface_key: asnDetailQuery
interface_name: 按ASN编号查询商品明细接口
---

## 按ASN编号查询商品明细接口 - 查询已添加的商品明细并提取detail_id

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | c5dae4866ba2436ea3e587f4ab5c8736 |
| 测试标题 | 按ASN编号查询明细-查询已添加的商品明细并提取detail_id |
| 前置条件 | 已成功创建 ASN 主单并添加商品明细；已提取 {{ ASN编号 }}、{{ 供应商名称 }}、{{ 商品编码 }}、{{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P0 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/detail/ |
| 请求方法 | GET |

### 请求头

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| Content-Type | application/json | JSON 请求头 |
| Accept | application/json | 期望 JSON 响应 |
| token | {{ 有效Token }} | GreaterWMS 认证凭据 |
| operator | {{ 操作员ID }} | 登录返回的 user_id |

### URL参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_code | {{ ASN编号 }} | ASN 编号，必填 |
| page | {{ 当前页码 }} | 页码，非必填 |
| max_page | {{ 分页大小 }} | 每页数量，非必填 |
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |

### 预期结果

- 响应状态码：200
- 响应格式：JSON
- count 等于 1
- results[0].asn_code 等于 {{ ASN编号 }}
- results[0].supplier 等于 {{ 供应商名称 }}
- results[0].goods_code 等于 {{ 商品编码 }}
- results[0].goods_qty 等于 {{ 计划数量 }}
- results[0].asn_status 等于 1
- results[0].goods_actual_qty 等于 0
- results[0].sorted_qty 等于 0
- results[0].id 为正整数
- 提取 detail_id=`$.results[0].id` 供后续上架用例使用
