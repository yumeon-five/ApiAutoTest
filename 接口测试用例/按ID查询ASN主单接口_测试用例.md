---
interface_key: asnListDetail
interface_name: 按ID查询ASN主单接口
---

## 按ID查询ASN主单接口 - 查询新建的ASN主单详情

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | b8c20adad7d04fc99a41befda1422e36 |
| 测试标题 | 按ID查询ASN主单-查询新建的ASN主单详情 |
| 前置条件 | 已成功登录并提取 {{ 有效Token }}、{{ 操作员ID }}；已通过创建接口提取 {{ ASN主键ID }}、{{ ASN编号 }}、{{ 条码 }} |
| 优先级 | P0 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/list/{{ ASN主键ID }}/ |
| 请求方法 | GET |

### 请求头

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| Content-Type | application/json | JSON 请求头 |
| Accept | application/json | 期望 JSON 响应 |
| token | {{ 有效Token }} | GreaterWMS 认证凭据（登录返回的 openid） |
| operator | {{ 操作员ID }} | 登录返回的 user_id |

### URL参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_id | {{ ASN主键ID }} | 路径参数，创建 ASN 响应中的 id，必填 |
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |

### 预期结果

- 响应状态码：200
- 响应格式：JSON
- 响应 id 等于 {{ ASN主键ID }}
- 响应 asn_code 与创建接口返回值一致
- 响应 bar_code 与创建接口返回值一致
- asn_status 等于 1
- creater 与创建接口请求体一致
- create_time 匹配正则 `^\d{4}-\d{2}-\d{2}`
