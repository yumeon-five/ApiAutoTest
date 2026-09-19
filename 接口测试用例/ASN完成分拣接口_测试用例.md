---
interface_key: asnSorted
interface_name: ASN完成分拣接口
---

## ASN完成分拣接口 - 状态3提交实到数量流转到状态4成功

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | e8f4b1431f8a4ede87973bdd29fbf321 |
| 测试标题 | ASN完成分拣-状态3提交实到数量流转到状态4成功 |
| 前置条件 | 已成功执行预分拣，ASN 当前状态为 3；已提取 {{ ASN主键ID }}、{{ ASN编号 }}、{{ 供应商名称 }}、{{ 商品编码 }}、{{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P0 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/sorted/{{ ASN主键ID }}/ |
| 请求方法 | POST |

### 请求头

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| Content-Type | application/json | JSON 请求体 |
| Accept | application/json | 期望 JSON 响应 |
| token | {{ 有效Token }} | GreaterWMS 认证凭据 |
| operator | {{ 操作员ID }} | 用于获取实际操作员工，必填 |

### URL参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_id | {{ ASN主键ID }} | 路径参数，状态 3 ASN 的主键，必填 |
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_code | {{ ASN编号 }} | ASN 编号，必填 |
| supplier | {{ 供应商名称 }} | 供应商名称，必填 |
| goodsData | [{"goods_code":"{{ 商品编码 }}","goods_actual_qty":{{ 实到数量 }}}] | 实际到货商品列表，必填 |
| creater | api_auto_{{ 运行标识 }} | 测试标识，非必填 |

### 预期结果

- 响应状态码：200
- 响应格式：JSON
- detail 等于 "success"
- 数据库 asnlist 与 asndetail 表对应记录 asn_status 均为 4
- 数据库 asndetail 表 goods_actual_qty 等于 {{ 实到数量 }}
- 数据库 stocklist 表对应商品 pre_sort_stock 减少 {{ 计划数量 }}
- 数据库 stocklist 表对应商品 sorted_stock 增加 {{ 实到数量 }}
- 数据库 stocklist 表 pre_load_stock、asn_stock 保持为 0

## ASN完成分拣接口 - 状态4重复提交分拣结果幂等拦截

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | a510e99a80ac4689891342336fdbd88a |
| 测试标题 | ASN完成分拣-状态4重复提交分拣结果幂等拦截 |
| 前置条件 | 已成功执行完成分拣，ASN 当前状态为 4；已提取 {{ ASN主键ID }}、{{ ASN编号 }}、{{ 供应商名称 }}、{{ 商品编码 }}、{{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P1 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/sorted/{{ ASN主键ID }}/ |
| 请求方法 | POST |

### 请求头

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| Content-Type | application/json | JSON 请求体 |
| Accept | application/json | 期望 JSON 响应 |
| token | {{ 有效Token }} | GreaterWMS 认证凭据 |
| operator | {{ 操作员ID }} | 用于获取实际操作员工，必填 |

### URL参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_id | {{ ASN主键ID }} | 路径参数，状态 4 ASN 的主键，必填 |
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_code | {{ ASN编号 }} | ASN 编号，必填 |
| supplier | {{ 供应商名称 }} | 供应商名称，必填 |
| goodsData | [{"goods_code":"{{ 商品编码 }}","goods_actual_qty":{{ 实到数量 }}}] | 重复提交相同实到数量 |

### 预期结果

- 响应状态码：200（当前源码异常处理缺陷）
- 响应格式：JSON
- 响应体 status_code 等于 500
- 响应体 detail 匹配 "This ASN Status Is Not 3"
- 数据库 asnlist 表 ASN 主单状态仍为 4
- 数据库 asndetail 表 goods_actual_qty 不得再次增加
- 数据库 stocklist 表 sorted_stock、pre_sort_stock 不得再次变化
