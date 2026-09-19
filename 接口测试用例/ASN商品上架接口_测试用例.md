---
interface_key: asnMoveToBin
interface_name: ASN商品上架接口
---

## ASN商品上架接口 - 上架数量等于0边界校验

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | ece328196eaa495a8f1ed2c98c92ab59 |
| 测试标题 | ASN商品上架-上架数量等于0边界校验 |
| 前置条件 | ASN 已完成分拣（状态 4，实到 {{ 实到数量 }} 件）；已提取 {{ ASN明细ID }}、{{ ASN编号 }}、{{ 商品编码 }}、{{ 库位名称 }}、{{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P2 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/movetobin/{{ ASN明细ID }}/ |
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
| detail_id | {{ ASN明细ID }} | 路径参数，状态 4 ASN 明细主键，必填 |
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_code | {{ ASN编号 }} | ASN 编号，必填 |
| goods_code | {{ 商品编码 }} | 商品编码，必填 |
| bin_name | {{ 库位名称 }} | Normal 库位，必填 |
| qty | 0 | 上架数量异常边界值 0 |

### 预期结果

- 响应状态码：200（当前源码异常处理缺陷）
- 响应格式：JSON
- 响应体 status_code 等于 500
- 响应体 detail 匹配 "Move QTY Must > 0"
- 数据库 asndetail 表 sorted_qty 仍为 0
- 数据库 stocklist 表对应商品 sorted_stock、onhand_stock、can_order_stock 均不发生变化
- 数据库 stockbin 表对应库位商品数量不发生变化
- 数据库数量变更记录表不得新增记录

## ASN商品上架接口 - 上架数量超过实到数量拦截

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 891dc79745f747538487bc8492d4f766 |
| 测试标题 | ASN商品上架-上架数量超过实到数量拦截 |
| 前置条件 | ASN 已完成分拣（状态 4，实到 {{ 实到数量 }}=10 件）；已提取 {{ ASN明细ID }}、{{ ASN编号 }}、{{ 商品编码 }}、{{ 库位名称 }}、{{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P1 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/movetobin/{{ ASN明细ID }}/ |
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
| detail_id | {{ ASN明细ID }} | 路径参数，状态 4 ASN 明细主键，必填 |
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_code | {{ ASN编号 }} | ASN 编号，必填 |
| goods_code | {{ 商品编码 }} | 商品编码，必填 |
| bin_name | {{ 库位名称 }} | Normal 库位，必填 |
| qty | {{ 超量上架数量 }} | 大于实到数量，取值 = {{ 实到数量 }} + 1（示例 11） |

### 预期结果

- 响应状态码：200（当前源码异常处理缺陷）
- 响应格式：JSON
- 响应体 status_code 等于 500
- 响应体 detail 匹配 "Move Qty must < Actual Arrive Qty"
- 数据库 asnlist 与 asndetail 表对应记录 asn_status 仍为 4
- 数据库 asndetail 表 sorted_qty 不发生变化
- 数据库 stocklist 表 onhand_stock、can_order_stock、sorted_stock 均不发生变化
- 数据库 stockbin 表对应库位商品数量不发生变化

## ASN商品上架接口 - 全量上架到Normal库位成功完成入库

### 用例信息

| 字段 | 内容 |
| ---- | ---- |
| 用例编号 | 8da3d3216bdc4f4fb8ec42ee104844a3 |
| 测试标题 | ASN商品上架-全量上架到Normal库位成功完成入库 |
| 前置条件 | ASN 已完成分拣（状态 4，实到 {{ 实到数量 }} 件）；已提取 {{ ASN明细ID }}、{{ ASN编号 }}、{{ 商品编码 }}、{{ 库位名称 }}（Normal 空库位）、{{ 有效Token }}、{{ 操作员ID }} |
| 优先级 | P0 |

### 请求信息

| 项目 | 内容 |
| ---- | ---- |
| 请求URL | {{ URL }}/asn/movetobin/{{ ASN明细ID }}/ |
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
| detail_id | {{ ASN明细ID }} | 路径参数，状态 4 ASN 明细主键，必填 |
| format | json | 响应格式 |

### 请求体参数

| 参数名 | 值 | 说明 |
| :----- | :--- | :--- |
| asn_code | {{ ASN编号 }} | ASN 编号，必填 |
| goods_code | {{ 商品编码 }} | 商品编码，必填 |
| bin_name | {{ 库位名称 }} | Normal 空库位，必填 |
| qty | {{ 上架数量 }} | 等于实际到货数量（示例 10） |

### 预期结果

- 响应状态码：200
- 响应格式：JSON
- detail 等于 "success"
- 数据库 asnlist 与 asndetail 表对应记录 asn_status 均为 5
- 数据库 asndetail 表 sorted_qty 等于 {{ 上架数量 }}
- 数据库 stocklist 表对应商品 sorted_stock 减少 {{ 上架数量 }}
- 数据库 stocklist 表对应商品 onhand_stock 增加 {{ 上架数量 }}
- 数据库 stocklist 表对应商品 can_order_stock 增加 {{ 上架数量 }}
- 数据库 stockbin 表对应库位由空变为非空且商品数量增加 {{ 上架数量 }}
- 数据库数量变更记录表新增 1 条上架流水
