---
interface_key: asnPreload
interface_name: ASN预装车接口
---

## ASN预装车接口 - 状态1携带明细流转到状态2成功

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 96d3b8b894b941c297b22fd2de2c354b |
| 测试标题 | ASN预装车-状态1携带明细流转到状态2成功 |
| 前置条件 | 已成功创建 ASN 主单（asn_status=1）并添加商品明细；已提取 {{ ASN主键ID }}、{{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P0 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/preload/{{ ASN主键ID }}/ |
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
| asn_id | {{ ASN主键ID }} | 路径参数，状态 1 ASN 的主键，必填 |
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |

### 预期结果

- 响应状态码：200
- 响应格式：JSON
- 响应 id 等于 {{ ASN主键ID }}
- asn_status 等于 2
- supplier 等于 {{ 供应商名称 }}
- 数据库 asnlist 与 asndetail 表对应记录 asn_status 同步为 2
- 数据库 stocklist 表对应商品 asn_stock 减少 {{ 计划数量 }}
- 数据库 stocklist 表对应商品 pre_load_stock 增加 {{ 计划数量 }}
- 数据库 stocklist 表对应商品 goods_qty、onhand_stock 保持不变

## ASN预装车接口 - 状态2重复预装车幂等拦截

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 38a5893863b141c999f9166b75e29030 |
| 测试标题 | ASN预装车-状态2重复预装车幂等拦截 |
| 前置条件 | 已成功执行预装车操作，ASN 当前状态为 2；已提取 {{ ASN主键ID }}、{{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P1 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/preload/{{ ASN主键ID }}/ |
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

- 响应状态码：200（当前源码异常处理缺陷）
- 响应格式：JSON
- 响应体 status_code 等于 500
- 响应体 detail 匹配 "This ASN Status Is Not 1"
- 数据库 asnlist 表 ASN 主单状态仍为 2
- 数据库 asndetail 表明细状态仍为 2
- 数据库 stocklist 表 asn_stock、pre_load_stock 不得再次变化
