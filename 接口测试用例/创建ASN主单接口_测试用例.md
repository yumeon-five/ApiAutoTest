---
interface_key: asnListCreate
interface_name: 创建ASN主单接口
---

## 创建ASN主单接口 - 携带有效Token与creater创建成功

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 9961cd44045d436696d7e517b9dd002a |
| 测试标题 | 创建ASN主单-携带有效Token与creater创建成功 |
| 前置条件 | 已成功登录并提取 {{ 有效Token }}、{{ 操作员ID }}；准备唯一测试运行标识 {{ 运行标识 }} |
| 优先级 | P0 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/list/ |
| 请求方法 | POST |

### 请求头

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| Content-Type | application/json | JSON 请求体 |
| Accept | application/json | 期望 JSON 响应 |
| token | {{ 有效Token }} | GreaterWMS 认证凭据（登录返回的 openid） |
| operator | {{ 操作员ID }} | 登录返回的 user_id |

### URL参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| creater | api_auto_{{ 运行标识 }} | 唯一测试运行标识，必填 |

### 预期结果

- 响应状态码：200
- 响应格式：JSON
- id 大于 0（JSONPath: `$.id`）
- asn_status 等于 1
- asn_code 以 "ASN" 开头（正则：`^ASN`）
- bar_code 存在且非空
- creater 等于请求体中的 creater
- create_time 匹配正则 `^\d{4}-\d{2}-\d{2}`
- 提取 asn_id=`$.id`、asn_code=`$.asn_code`、bar_code=`$.bar_code` 供后续状态流转用例使用

## 创建ASN主单接口 - 请求体缺少必填creater字段

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | fa637f98fba14ceb94edb943e6daf0af |
| 测试标题 | 创建ASN主单-请求体缺少必填creater字段 |
| 前置条件 | 已成功登录并提取 {{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P1 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/list/ |
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
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |

### 预期结果

- 响应状态码：200（当前源码异常处理缺陷，修复后应断言 HTTP 400）
- 响应格式：JSON
- 响应体 status_code 等于 400
- 响应体包含 creater 字段必填错误提示（如 "This field is required."）
- 数据库 asnlist 表不得新增记录
- 数据库 scanner 表不得新增条码记录

## 创建ASN主单接口 - creater包含script等危险字符串被拦截

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 69c42ee2131847859d6342144efff472 |
| 测试标题 | 创建ASN主单-creater包含script等危险字符串被拦截 |
| 前置条件 | 已成功登录并提取 {{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P1 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/list/ |
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
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| creater | {{ 危险字符串 }} | 危险输入，建议取值 `<script>alert(1)</script>` 或包含 select/insert 等 SQL 关键字 |

### 预期结果

- 响应状态码：200（当前源码异常处理缺陷，修复后应断言 HTTP 4xx/5xx）
- 响应格式：JSON
- 响应体 status_code 等于 500
- 响应体 detail 匹配 "Bad Data can‘not be store" 或包含危险输入拦截提示
- 数据库 asnlist 表不得新增对应记录
- 数据库 scanner 表不得新增对应条码记录
