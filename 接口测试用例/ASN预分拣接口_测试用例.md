---
interface_key: asnPresort
interface_name: ASN预分拣接口
---

## ASN预分拣接口 - 状态2流转到状态3成功

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 86836a07862b4f8293647ccda02c0075 |
| 测试标题 | ASN预分拣-状态2流转到状态3成功 |
| 前置条件 | 已成功执行预装车，ASN 当前状态为 2；已提取 {{ ASN主键ID }}、{{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P0 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/presort/{{ ASN主键ID }}/ |
| 请求方法 | POST |

### 请求头

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| Content-Type | application/json | JSON 请求体 |
| Accept | application/json | 期望 JSON 响应 |
| token | {{ 有效Token }} | GreaterWMS 认证凭据 |
| operator | {{ 操作员ID }} | 登录返回的 user_id |

### URL参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_id | {{ ASN主键ID }} | 路径参数，状态 2 ASN 的主键，必填 |
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |

### 预期结果

- 响应状态码：200
- 响应格式：JSON
- 响应 id 等于 {{ ASN主键ID }}
- asn_status 等于 3
- supplier 等于 {{ 供应商名称 }}
- 数据库 asnlist 与 asndetail 表对应记录 asn_status 同步为 3
- 数据库 stocklist 表对应商品 pre_load_stock 减少 {{ 计划数量 }}
- 数据库 stocklist 表对应商品 pre_sort_stock 增加 {{ 计划数量 }}
- 数据库 stocklist 表 asn_stock 保持为 0

## ASN预分拣接口 - 状态3重复预分拣幂等拦截

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 3d8ff98d091143c4ab603632cb7aaaf1 |
| 测试标题 | ASN预分拣-状态3重复预分拣幂等拦截 |
| 前置条件 | 已成功执行预分拣操作，ASN 当前状态为 3；已提取 {{ ASN主键ID }}、{{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P1 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/presort/{{ ASN主键ID }}/ |
| 请求方法 | POST |

### 请求头

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| Content-Type | application/json | JSON 请求体 |
| Accept | application/json | 期望 JSON 响应 |
| token | {{ 有效Token }} | GreaterWMS 认证凭据 |
| operator | {{ 操作员ID }} | 登录返回的 user_id |

### URL参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_id | {{ ASN主键ID }} | 路径参数，状态 3 ASN 的主键，必填 |
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |

### 预期结果

- 响应状态码：200（当前源码异常处理缺陷）
- 响应格式：JSON
- 响应体 status_code 等于 500
- 响应体 detail 匹配 "This ASN Status Is Not 2"
- 数据库 asnlist 表 ASN 主单状态仍为 3
- 数据库 stocklist 表 pre_load_stock、pre_sort_stock 不得再次变化
