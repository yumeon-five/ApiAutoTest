---
interface_key: asnDetailCreate
interface_name: 添加ASN商品明细接口
---

## 添加ASN商品明细接口 - 状态1ASN添加单条有效商品明细成功

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 18c0a9ee2223421182d82e423817ecff |
| 测试标题 | 添加ASN商品明细-状态1ASN添加单条有效商品明细成功 |
| 前置条件 | 已成功创建 ASN 主单（asn_status=1）并提取 {{ ASN编号 }}；已提取 {{ 供应商名称 }}、{{ 商品编码 }}、{{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P0 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/detail/ |
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
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_code | {{ ASN编号 }} | ASN 编号，必填 |
| supplier | {{ 供应商名称 }} | 有效供应商名称，必填 |
| goods_code | ["{{ 商品编码 }}"] | 商品编码数组，必填 |
| goods_qty | [{{ 计划数量 }}] | 计划数量数组，与 goods_code 一一对应，必填 |
| creater | api_auto_{{ 运行标识 }} | 测试运行标识，非必填 |

### 预期结果

- 响应状态码：200
- 响应格式：JSON
- detail 等于 "success"
- 数据库 asndetail 表新增 1 条 goods_qty 等于 {{ 计划数量 }}、asn_status=1 的明细记录
- 数据库 stocklist 表对应商品的 goods_qty 增加 {{ 计划数量 }}
- 数据库 stocklist 表对应商品的 asn_stock 增加 {{ 计划数量 }}
- 数据库 stocklist 表对应商品的 onhand_stock、can_order_stock 保持不变

## 添加ASN商品明细接口 - ASN编号不存在关联校验失败

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 60f2fdf269254643a16aeac6c74841f9 |
| 测试标题 | 添加ASN商品明细-ASN编号不存在关联校验失败 |
| 前置条件 | 已成功登录并提取 {{ 有效Token }}、{{ 操作员ID }}、{{ 供应商名称 }}、{{ 商品编码 }} |
| 优先级 | P1 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/detail/ |
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
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_code | {{ 不存在的ASN编号 }} | 不存在的 ASN 编号，建议格式 `ASN_NOT_EXISTS_{{ 运行标识 }}` |
| supplier | {{ 供应商名称 }} | 有效供应商名称 |
| goods_code | ["{{ 商品编码 }}"] | 有效商品编码数组 |
| goods_qty | [{{ 计划数量 }}] | 计划数量数组 |

### 预期结果

- 响应状态码：200（当前源码异常处理缺陷，修复后应断言 HTTP 4xx/5xx）
- 响应格式：JSON
- 响应体 status_code 等于 500
- 响应体 detail 匹配 "ASN Code does not exists"
- 数据库 asndetail 表不得新增记录
- 数据库 stocklist 表对应商品库存不发生变化

## 添加ASN商品明细接口 - 供应商不存在关联校验失败

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 96b20b3655434c1f8066dd07157ca00d |
| 测试标题 | 添加ASN商品明细-供应商不存在关联校验失败 |
| 前置条件 | 已成功创建 ASN 主单并提取 {{ ASN编号 }}；已提取 {{ 有效Token }}、{{ 操作员ID }}、{{ 商品编码 }} |
| 优先级 | P1 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/detail/ |
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
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_code | {{ ASN编号 }} | 有效 ASN 编号 |
| supplier | {{ 不存在的供应商 }} | 不存在的供应商，建议格式 `SUPPLIER_NOT_EXISTS_{{ 运行标识 }}` |
| goods_code | ["{{ 商品编码 }}"] | 有效商品编码数组 |
| goods_qty | [{{ 计划数量 }}] | 计划数量数组 |

### 预期结果

- 响应状态码：200（当前源码异常处理缺陷，修复后应断言 HTTP 4xx/5xx）
- 响应格式：JSON
- 响应体 status_code 等于 500
- 响应体 detail 匹配 "Supplier does not exists"
- ASN 主单状态仍为 1
- 数据库 asndetail 表不得新增记录
- 数据库 stocklist 表对应商品库存不发生变化

## 添加ASN商品明细接口 - 计划数量等于0边界值校验

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 16b896c071fa4b5ebd89480d5e151c8f |
| 测试标题 | 添加ASN商品明细-计划数量等于0边界值校验 |
| 前置条件 | 已成功创建 ASN 主单并提取 {{ ASN编号 }}；已提取 {{ 供应商名称 }}、{{ 商品编码 }}、{{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P2 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/detail/ |
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
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_code | {{ ASN编号 }} | 有效 ASN 编号 |
| supplier | {{ 供应商名称 }} | 有效供应商名称 |
| goods_code | ["{{ 商品编码 }}"] | 有效商品编码数组 |
| goods_qty | [0] | 计划数量边界值 0 |

### 预期结果

- 响应状态码：200（当前源码异常处理缺陷）
- 响应格式：JSON
- 响应体 status_code 等于 500
- 响应体 detail 匹配 "Qty Must > 0"
- 数据库 asndetail 表不得新增记录
- 数据库 stocklist 表对应商品库存不发生变化

## 添加ASN商品明细接口 - 计划数量为负数异常校验

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 3d05008a43594edea7d67ee521a115e8 |
| 测试标题 | 添加ASN商品明细-计划数量为负数异常校验 |
| 前置条件 | 已成功创建 ASN 主单并提取 {{ ASN编号 }}；已提取 {{ 供应商名称 }}、{{ 商品编码 }}、{{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P2 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/detail/ |
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
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_code | {{ ASN编号 }} | 有效 ASN 编号 |
| supplier | {{ 供应商名称 }} | 有效供应商名称 |
| goods_code | ["{{ 商品编码 }}"] | 有效商品编码数组 |
| goods_qty | [-1] | 计划数量负数异常值 |

### 预期结果

- 响应状态码：200（当前源码异常处理缺陷）
- 响应格式：JSON
- 响应体 status_code 等于 500
- 响应体 detail 匹配 "Qty Must > 0"
- 数据库 asndetail 表不得新增记录
- 数据库 stocklist 表对应商品库存不得出现负数
- 数据库 stocklist 表 asn_stock、goods_qty 不发生变化
