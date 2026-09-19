---
interface_key: asnListQuery
interface_name: 查询ASN主单列表接口
---

## 查询ASN主单列表接口 - 未携带Token鉴权失败

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 89c816ed5354465ea6780fa93e94137b |
| 测试标题 | 查询ASN列表-未携带Token鉴权失败 |
| 前置条件 | 无 |
| 优先级 | P1 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/list/ |
| 请求方法 | GET |

### 请求头

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| Accept | application/json | 期望 JSON 响应；本用例故意不携带 token |

### URL参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| page | {{ 当前页码 }} | 页码，非必填 |
| max_page | {{ 分页大小 }} | 每页数量，非必填 |
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |

### 预期结果

- 响应状态码：200（当前源码异常处理缺陷，修复后应断言 HTTP 401/403）
- 响应格式：JSON
- 响应体 status_code 等于 500
- 响应体 detail 匹配 "Please Add Token To Your Request Headers"
- 响应体不得返回任何 ASN 业务数据（无 results / count 字段）

## 查询ASN主单列表接口 - 按asn_code精确筛选当前用户ASN主单

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 2a2c0996b04443208e2d5a538b8e14ac |
| 测试标题 | 查询ASN列表-按asn_code精确筛选当前用户ASN主单 |
| 前置条件 | 已成功登录并提取 {{ 有效Token }}、{{ 操作员ID }}；已通过创建接口提取 {{ ASN编号 }} |
| 优先级 | P0 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/list/ |
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
| asn_code | {{ ASN编号 }} | 创建接口提取的 ASN 编号，必填 |
| page | {{ 当前页码 }} | 页码，非必填 |
| max_page | {{ 分页大小 }} | 每页数量，非必填 |
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |

### 预期结果

- 响应状态码：200
- 响应格式：JSON
- count 至少为 1
- results 数组中存在 asn_code 完全等于 {{ ASN编号 }} 的记录
- 命中记录的 asn_status 等于 1
- 命中记录的 creater 与创建请求一致
- 响应体不得返回其他用户的 ASN 数据
