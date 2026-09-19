# GreaterWMS ASN 入库链路 30 条标准接口文档

> 本文按“基本信息—请求参数—请求示例—返回数据”的统一格式编写。
> 每个编号对应 1 条 Allure 测试用例；30 条用例涉及约 15 类接口路由，正常场景 16 条、异常场景 14 条。
> 文中的 ${变量名} 为接口自动化框架运行时变量；响应示例只展示断言所需的核心字段。

## 使用说明

- 默认服务地址：http://127.0.0.1:8008
- 登录成功后提取 token=$.data.openid、operator=$.data.user_id。
- GreaterWMS 当前异常处理器会把外层 HTTP 状态重置为 200，原异常状态放在响应体 status_code 中；本文按当前源码实际行为记录。
- POST /asn/detail/ 的 goods_code、goods_qty 实际为数组；分拣使用 goodsData 数组；这些均以源码真实请求为准。

## 1、登录成功（AUTH-001）

#### 基本信息

- **Path：** /login/
- **Method：** POST
- **接口描述：** 使用正确账号密码登录，获取后续业务接口需要的 token（openid）和 operator（user_id）。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | 是 | application/json | JSON 请求体 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| name | string | 是 | ${username} | 登录用户名 |
| password | string | 是 | ${password} | 登录密码 |

**请求示例**

~~~json
{
  "name": "${username}",
  "password": "${password}"
}
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "code": "200",
  "msg": "Success Create",
  "ip": "127.0.0.1",
  "data": {
    "name": "${username}",
    "openid": "9f3c...示例openid",
    "user_id": 1
  }
}
~~~

- **断言要点：** code 等于 "200"；data.openid 非空；data.user_id 为正整数。提取 token=$.data.openid、operator=$.data.user_id。

## 2、登录失败—密码错误（AUTH-002）

#### 基本信息

- **Path：** /login/
- **Method：** POST
- **接口描述：** 用户名存在但密码错误，验证登录失败提示及不返回认证凭据。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | 是 | application/json | JSON 请求体 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| name | string | 是 | ${username} | 正确用户名 |
| password | string | 是 | wrong_password | 故意传入错误密码 |

**请求示例**

~~~json
{
  "name": "${username}",
  "password": "wrong_password"
}
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "code": "1011",
  "msg": "User Name Or Password Error",
  "data": {
    "name": "${username}",
    "password": "wrong_password"
  }
}
~~~

- **断言要点：** code 等于 "1011"；msg 匹配错误文案；响应中不得出现 openid。当前源码会回显 password，属于待修复的安全问题。

## 3、登录失败—缺少密码（AUTH-003）

#### 基本信息

- **Path：** /login/
- **Method：** POST
- **接口描述：** 验证请求体缺少 password 时的处理结果。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | 是 | application/json | JSON 请求体 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| name | string | 是 | ${username} | 正确用户名 |
| password | string | 是 | 不传 | 本异常用例故意省略 |

**请求示例**

~~~json
{
  "name": "${username}"
}
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "code": "1011",
  "msg": "User Name Or Password Error",
  "data": {
    "name": "${username}",
    "password": null
  }
}
~~~

- **断言要点：** code 等于 "1011"；msg 匹配错误文案；不得返回 token。

## 4、鉴权失败—未携带 Token（AUTH-004）

#### 基本信息

- **Path：** /asn/list/
- **Method：** GET
- **接口描述：** 不携带 token 请求 ASN 列表，验证业务接口鉴权。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | 不传 | 是 | 本用例故意省略 | 验证未认证访问 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| page | integer | 否 | 1 | 页码 |
| max_page | integer | 否 | 20 | 每页数量 |
| format | string | 否 | json | 响应格式 |

**body**

无业务字段。POST 时发送空 JSON 对象 `{}`。

**请求示例**

~~~http
GET /asn/list/?page=1&max_page=20&format=json
~~~

#### 返回数据

- **响应状态码：** 200（当前源码异常处理缺陷）
- **响应数据：**

~~~json
{
  "detail": "Please Add Token To Your Request Headers",
  "status_code": 500
}
~~~

- **断言要点：** 响应体 status_code 等于 500，detail 匹配。后端异常处理修复后，应改为断言真实 HTTP 401/403。

## 5、查询可用供应商（BASE-001）

#### 基本信息

- **Path：** /supplier/
- **Method：** GET
- **接口描述：** 查询当前用户可用供应商，为创建 ASN 明细提取 supplier_name。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| page | integer | 否 | 1 | 页码 |
| max_page | integer | 否 | 20 | 每页数量 |
| format | string | 否 | json | 响应格式 |

**body**

无业务字段。POST 时发送空 JSON 对象 `{}`。

**请求示例**

~~~http
GET /supplier/?page=1&max_page=20&format=json
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "supplier_name": "测试供应商",
      "supplier_city": "上海",
      "supplier_address": "测试地址",
      "supplier_contact": "13800000000"
    }
  ]
}
~~~

- **断言要点：** count 大于 0；results[0].supplier_name 非空。提取 supplier_name=$.results[0].supplier_name。

## 6、查询可用商品（BASE-002）

#### 基本信息

- **Path：** /goods/
- **Method：** GET
- **接口描述：** 查询当前用户可用商品，为 ASN 明细和库存校验提取 goods_code。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| page | integer | 否 | 1 | 页码 |
| max_page | integer | 否 | 20 | 每页数量 |
| format | string | 否 | json | 响应格式 |

**body**

无业务字段。POST 时发送空 JSON 对象 `{}`。

**请求示例**

~~~http
GET /goods/?page=1&max_page=20&format=json
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "goods_code": "G0001",
      "goods_desc": "测试商品",
      "goods_weight": 1000,
      "goods_cost": 20
    }
  ]
}
~~~

- **断言要点：** count 大于 0；goods_code、goods_desc 非空。提取 goods_code=$.results[0].goods_code。

## 7、查询普通空库位（BASE-003）

#### 基本信息

- **Path：** /binset/
- **Method：** GET
- **接口描述：** 筛选 Normal 类型且尚未占用的库位，为最终上架提取 bin_name。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| bin_property | string | 是 | Normal | 库位属性 |
| empty_label | boolean | 是 | true | 是否为空库位 |
| page | integer | 否 | 1 | 页码 |
| max_page | integer | 否 | 20 | 每页数量 |
| format | string | 否 | json | 响应格式 |

**body**

无业务字段。POST 时发送空 JSON 对象 `{}`。

**请求示例**

~~~http
GET /binset/?bin_property=Normal&empty_label=true&page=1&max_page=20&format=json
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "bin_name": "A01-01-01",
      "bin_size": "Big",
      "bin_property": "Normal",
      "empty_label": true
    }
  ]
}
~~~

- **断言要点：** count 大于 0；bin_property 等于 Normal；empty_label 为 true。提取 bin_name=$.results[0].bin_name。

## 8、获取商品库存基线（BASE-004）

#### 基本信息

- **Path：** /stock/list/
- **Method：** GET
- **接口描述：** 在创建 ASN 明细前读取商品库存，保存各库存字段作为后续增量断言基线。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| goods_code | string | 是 | ${goods_code} | 从商品接口提取 |
| page | integer | 否 | 1 | 页码 |
| max_page | integer | 否 | 20 | 每页数量 |
| format | string | 否 | json | 响应格式 |

**body**

无业务字段。POST 时发送空 JSON 对象 `{}`。

**请求示例**

~~~http
GET /stock/list/?goods_code=${goods_code}&page=1&max_page=20&format=json
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 301,
      "goods_code": "G0001",
      "goods_desc": "测试商品",
      "goods_qty": 10,
      "onhand_stock": 0,
      "can_order_stock": 0,
      "inspect_stock": 0,
      "hold_stock": 0,
      "damage_stock": 0,
      "asn_stock": 10,
      "dn_stock": 0,
      "pre_load_stock": 0,
      "pre_sort_stock": 0,
      "sorted_stock": 0,
      "pick_stock": 0,
      "picked_stock": 0,
      "back_order_stock": 0
    }
  ]
}
~~~

- **断言要点：** results 为数组且 goods_code 匹配；保存 goods_qty、onhand_stock、can_order_stock 和各阶段库存。count=0 时基线按 0 处理。

## 9、创建 ASN 主单成功（ASN-LIST-001）

#### 基本信息

- **Path：** /asn/list/
- **Method：** POST
- **接口描述：** 创建 ASN 入库主单。asn_code、bar_code、openid 由服务端生成。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| creater | string | 是 | api_auto_20260918_001 | 唯一测试运行标识 |

**请求示例**

~~~json
{
  "creater": "api_auto_${run_id}"
}
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "id": 101,
  "asn_code": "ASN20260918001",
  "asn_status": 1,
  "total_weight": 0,
  "total_volume": 0,
  "total_cost": 0,
  "supplier": "",
  "creater": "api_auto_20260918_001",
  "bar_code": "4b1c...示例条码",
  "transportation_fee": {},
  "create_time": "2026-09-18 10:00:00",
  "update_time": "2026-09-18 10:00:00"
}
~~~

- **断言要点：** id 大于 0；asn_status 等于 1；asn_code 以 ASN 开头；bar_code 非空。提取 asn_id、asn_code、bar_code。

## 10、按 ID 查询 ASN（ASN-LIST-002）

#### 基本信息

- **Path：** /asn/list/{asn_id}/
- **Method：** GET
- **接口描述：** 根据创建接口返回的 ASN 主键查询单条主单。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**path**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_id | integer | 是 | ${asn_id} | 创建 ASN 响应中的 id |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

无业务字段。POST 时发送空 JSON 对象 `{}`。

**请求示例**

~~~http
GET /asn/list/${asn_id}/?format=json
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "id": 101,
  "asn_code": "ASN20260918001",
  "asn_status": 1,
  "total_weight": 0,
  "total_volume": 0,
  "total_cost": 0,
  "supplier": "",
  "creater": "api_auto_20260918_001",
  "bar_code": "4b1c...示例条码",
  "transportation_fee": {},
  "create_time": "2026-09-18 10:00:00",
  "update_time": "2026-09-18 10:00:00"
}
~~~

- **断言要点：** 响应 id、asn_code、bar_code 与创建结果一致，asn_status 等于 1。

## 11、按 ASN 编号筛选列表（ASN-LIST-003）

#### 基本信息

- **Path：** /asn/list/
- **Method：** GET
- **接口描述：** 使用 asn_code 精确筛选当前用户的 ASN 主单。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_code | string | 是 | ${asn_code} | 创建接口提取的 ASN 编号 |
| page | integer | 否 | 1 | 页码 |
| max_page | integer | 否 | 20 | 每页数量 |
| format | string | 否 | json | 响应格式 |

**body**

无业务字段。POST 时发送空 JSON 对象 `{}`。

**请求示例**

~~~http
GET /asn/list/?asn_code=${asn_code}&page=1&max_page=20&format=json
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "supplier_list": [],
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 101,
      "asn_code": "ASN20260918001",
      "asn_status": 1,
      "total_weight": 0,
      "total_volume": 0,
      "total_cost": 0,
      "supplier": "",
      "creater": "api_auto_20260918_001",
      "bar_code": "4b1c...示例条码",
      "transportation_fee": {},
      "create_time": "2026-09-18 10:00:00",
      "update_time": "2026-09-18 10:00:00"
    }
  ]
}
~~~

- **断言要点：** count 至少为 1；结果中存在 asn_code 完全相同的记录；不得返回其他用户数据。

## 12、创建 ASN 失败—缺少 creater（ASN-LIST-004）

#### 基本信息

- **Path：** /asn/list/
- **Method：** POST
- **接口描述：** 验证创建 ASN 时缺少必填创建人字段的参数校验。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| creater | string | 是 | 不传 | 本异常用例故意省略 |

**请求示例**

~~~json
{}
~~~

#### 返回数据

- **响应状态码：** 200（当前源码异常处理缺陷）
- **响应数据：**

~~~json
{
  "creater": [
    "This field is required."
  ],
  "status_code": 400
}
~~~

- **断言要点：** 响应体 status_code 等于 400，并包含 creater 必填错误；数据库不得新增 ASN。

## 13、创建 ASN 失败—危险字符串（ASN-LIST-005）

#### 基本信息

- **Path：** /asn/list/
- **Method：** POST
- **接口描述：** 验证 creater 中包含 script/select 关键字时的输入过滤。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| creater | string | 是 | <script>alert(1)</script> | 危险输入 |

**请求示例**

~~~json
{
  "creater": "<script>alert(1)</script>"
}
~~~

#### 返回数据

- **响应状态码：** 200（当前源码异常处理缺陷）
- **响应数据：**

~~~json
{
  "detail": "Bad Data can‘not be store",
  "status_code": 500
}
~~~

- **断言要点：** 响应体 status_code 等于 500，detail 匹配；asnlist 和 scanner 表均不得新增对应数据。

## 14、添加 ASN 商品明细成功（ASN-DETAIL-001）

#### 基本信息

- **Path：** /asn/detail/
- **Method：** POST
- **接口描述：** 给状态 1 的 ASN 添加一条商品明细。源码实际要求 goods_code、goods_qty 使用数组。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 是 | 登录返回的 user_id | 用于获取实际操作员工 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_code | string | 是 | ${asn_code} | ASN 编号 |
| supplier | string | 是 | ${supplier_name} | 有效供应商名称 |
| goods_code | array[string] | 是 | ["G0001"] | 商品编码数组 |
| goods_qty | array[integer] | 是 | [10] | 计划数量数组，与 goods_code 一一对应 |
| creater | string | 否 | api_auto_20260918_001 | 源码最终使用 operator 对应员工 |

**请求示例**

~~~json
{
  "asn_code": "${asn_code}",
  "supplier": "${supplier_name}",
  "goods_code": [
    "${goods_code}"
  ],
  "goods_qty": [
    10
  ],
  "creater": "api_auto_${run_id}"
}
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "detail": "success"
}
~~~

- **断言要点：** detail 等于 success；asndetail 新增数量 10 的状态 1 明细；stocklist.goods_qty 和 asn_stock 各增加 10。

## 15、按 ASN 编号查询明细（ASN-DETAIL-002）

#### 基本信息

- **Path：** /asn/detail/
- **Method：** GET
- **接口描述：** 根据 asn_code 查询商品明细，并提取后续上架所需的 detail_id。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_code | string | 是 | ${asn_code} | ASN 编号 |
| page | integer | 否 | 1 | 页码 |
| max_page | integer | 否 | 20 | 每页数量 |
| format | string | 否 | json | 响应格式 |

**body**

无业务字段。POST 时发送空 JSON 对象 `{}`。

**请求示例**

~~~http
GET /asn/detail/?asn_code=${asn_code}&page=1&max_page=20&format=json
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 201,
      "asn_code": "ASN20260918001",
      "asn_status": 1,
      "supplier": "测试供应商",
      "goods_code": "G0001",
      "goods_desc": "测试商品",
      "goods_qty": 10,
      "goods_actual_qty": 0,
      "sorted_qty": 0,
      "goods_shortage_qty": 0,
      "goods_more_qty": 0,
      "goods_damage_qty": 0,
      "creater": "测试员工",
      "create_time": "2026-09-18 10:01:00",
      "update_time": "2026-09-18 10:01:00"
    }
  ]
}
~~~

- **断言要点：** count 等于 1；asn_code、supplier、goods_code、goods_qty 与创建请求一致。提取 detail_id=$.results[0].id。

## 16、添加明细失败—ASN 不存在（ASN-DETAIL-003）

#### 基本信息

- **Path：** /asn/detail/
- **Method：** POST
- **接口描述：** 使用不存在的 ASN 编号添加商品明细，验证主单关联校验。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 是 | 登录返回的 user_id | 用于获取实际操作员工 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_code | string | 是 | ASN_NOT_EXISTS_001 | 不存在的 ASN 编号 |
| supplier | string | 是 | ${supplier_name} | 有效供应商 |
| goods_code | array[string] | 是 | ["G0001"] | 有效商品 |
| goods_qty | array[integer] | 是 | [10] | 计划数量 |

**请求示例**

~~~json
{
  "asn_code": "ASN_NOT_EXISTS_${run_id}",
  "supplier": "${supplier_name}",
  "goods_code": [
    "${goods_code}"
  ],
  "goods_qty": [
    10
  ]
}
~~~

#### 返回数据

- **响应状态码：** 200（当前源码异常处理缺陷）
- **响应数据：**

~~~json
{
  "detail": "ASN Code does not exists",
  "status_code": 500
}
~~~

- **断言要点：** 响应体 status_code 等于 500，detail 匹配；asndetail 不新增，库存不变化。

## 17、添加明细失败—供应商不存在（ASN-DETAIL-004）

#### 基本信息

- **Path：** /asn/detail/
- **Method：** POST
- **接口描述：** 对有效 ASN 使用不存在的供应商，验证供应商关联校验。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 是 | 登录返回的 user_id | 用于获取实际操作员工 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_code | string | 是 | ${asn_code} | 有效 ASN |
| supplier | string | 是 | SUPPLIER_NOT_EXISTS_001 | 不存在的供应商 |
| goods_code | array[string] | 是 | ["G0001"] | 有效商品 |
| goods_qty | array[integer] | 是 | [10] | 计划数量 |

**请求示例**

~~~json
{
  "asn_code": "${asn_code}",
  "supplier": "SUPPLIER_NOT_EXISTS_${run_id}",
  "goods_code": [
    "${goods_code}"
  ],
  "goods_qty": [
    10
  ]
}
~~~

#### 返回数据

- **响应状态码：** 200（当前源码异常处理缺陷）
- **响应数据：**

~~~json
{
  "detail": "Supplier does not exists",
  "status_code": 500
}
~~~

- **断言要点：** 响应体 status_code 等于 500，detail 匹配；ASN 仍为状态 1，明细和库存不变化。

## 18、添加明细失败—数量为 0（ASN-DETAIL-005）

#### 基本信息

- **Path：** /asn/detail/
- **Method：** POST
- **接口描述：** 验证计划入库数量等于 0 时的边界校验。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 是 | 登录返回的 user_id | 用于获取实际操作员工 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_code | string | 是 | ${asn_code} | 有效 ASN |
| supplier | string | 是 | ${supplier_name} | 有效供应商 |
| goods_code | array[string] | 是 | ["G0001"] | 有效商品 |
| goods_qty | array[integer] | 是 | [0] | 边界值 0 |

**请求示例**

~~~json
{
  "asn_code": "${asn_code}",
  "supplier": "${supplier_name}",
  "goods_code": [
    "${goods_code}"
  ],
  "goods_qty": [
    0
  ]
}
~~~

#### 返回数据

- **响应状态码：** 200（当前源码异常处理缺陷）
- **响应数据：**

~~~json
{
  "detail": "Qty Must > 0",
  "status_code": 500
}
~~~

- **断言要点：** 响应体 status_code 等于 500，detail 匹配；不得新增明细或修改库存。

## 19、添加明细失败—数量为负数（ASN-DETAIL-006）

#### 基本信息

- **Path：** /asn/detail/
- **Method：** POST
- **接口描述：** 验证计划入库数量小于 0 时的异常校验。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 是 | 登录返回的 user_id | 用于获取实际操作员工 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_code | string | 是 | ${asn_code} | 有效 ASN |
| supplier | string | 是 | ${supplier_name} | 有效供应商 |
| goods_code | array[string] | 是 | ["G0001"] | 有效商品 |
| goods_qty | array[integer] | 是 | [-1] | 负数异常值 |

**请求示例**

~~~json
{
  "asn_code": "${asn_code}",
  "supplier": "${supplier_name}",
  "goods_code": [
    "${goods_code}"
  ],
  "goods_qty": [
    -1
  ]
}
~~~

#### 返回数据

- **响应状态码：** 200（当前源码异常处理缺陷）
- **响应数据：**

~~~json
{
  "detail": "Qty Must > 0",
  "status_code": 500
}
~~~

- **断言要点：** 响应体 status_code 等于 500，detail 匹配；不得新增明细，库存不得出现负数。

## 20、预装车成功（ASN-PRELOAD-001）

#### 基本信息

- **Path：** /asn/preload/{asn_id}/
- **Method：** POST
- **接口描述：** 将包含明细的 ASN 从状态 1 流转到状态 2。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**path**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_id | integer | 是 | ${asn_id} | 状态 1 ASN 的主键 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

无业务字段。POST 时发送空 JSON 对象 `{}`。

**请求示例**

~~~json
{}
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "id": 101,
  "asn_code": "ASN20260918001",
  "asn_status": 2,
  "total_weight": 0,
  "total_volume": 0,
  "total_cost": 0,
  "supplier": "测试供应商",
  "creater": "api_auto_20260918_001",
  "bar_code": "4b1c...示例条码",
  "transportation_fee": {},
  "create_time": "2026-09-18 10:00:00",
  "update_time": "2026-09-18 10:00:00"
}
~~~

- **断言要点：** asn_status 等于 2；主单和明细状态同步；asn_stock 减 10，pre_load_stock 加 10。

## 21、预装车失败—重复操作（ASN-PRELOAD-002）

#### 基本信息

- **Path：** /asn/preload/{asn_id}/
- **Method：** POST
- **接口描述：** 对已处于状态 2 的 ASN 再次预装车，验证状态机与幂等保护。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**path**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_id | integer | 是 | ${asn_id} | 状态 2 ASN 的主键 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

无业务字段。POST 时发送空 JSON 对象 `{}`。

**请求示例**

~~~json
{}
~~~

#### 返回数据

- **响应状态码：** 200（当前源码异常处理缺陷）
- **响应数据：**

~~~json
{
  "detail": "This ASN Status Is Not 1",
  "status_code": 500
}
~~~

- **断言要点：** 响应体 status_code 等于 500；状态仍为 2；阶段库存不得再次变化。

## 22、预分拣成功（ASN-PRESORT-001）

#### 基本信息

- **Path：** /asn/presort/{asn_id}/
- **Method：** POST
- **接口描述：** 将 ASN 从状态 2 流转到状态 3。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**path**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_id | integer | 是 | ${asn_id} | 状态 2 ASN 的主键 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

无业务字段。POST 时发送空 JSON 对象 `{}`。

**请求示例**

~~~json
{}
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "id": 101,
  "asn_code": "ASN20260918001",
  "asn_status": 3,
  "total_weight": 0,
  "total_volume": 0,
  "total_cost": 0,
  "supplier": "测试供应商",
  "creater": "api_auto_20260918_001",
  "bar_code": "4b1c...示例条码",
  "transportation_fee": {},
  "create_time": "2026-09-18 10:00:00",
  "update_time": "2026-09-18 10:00:00"
}
~~~

- **断言要点：** asn_status 等于 3；pre_load_stock 减 10，pre_sort_stock 加 10。

## 23、预分拣失败—重复操作（ASN-PRESORT-002）

#### 基本信息

- **Path：** /asn/presort/{asn_id}/
- **Method：** POST
- **接口描述：** 对已处于状态 3 的 ASN 再次预分拣，验证状态机与幂等保护。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**path**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_id | integer | 是 | ${asn_id} | 状态 3 ASN 的主键 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

无业务字段。POST 时发送空 JSON 对象 `{}`。

**请求示例**

~~~json
{}
~~~

#### 返回数据

- **响应状态码：** 200（当前源码异常处理缺陷）
- **响应数据：**

~~~json
{
  "detail": "This ASN Status Is Not 2",
  "status_code": 500
}
~~~

- **断言要点：** 响应体 status_code 等于 500；状态仍为 3；阶段库存不得再次变化。

## 24、完成分拣成功（ASN-SORTED-001）

#### 基本信息

- **Path：** /asn/sorted/{asn_id}/
- **Method：** POST
- **接口描述：** 提交实际到货数量，计划 10、实到 10，将 ASN 从状态 3 流转到状态 4。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 是 | 登录返回的 user_id | 用于获取实际操作员工 |

**path**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_id | integer | 是 | ${asn_id} | 状态 3 ASN 的主键 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_code | string | 是 | ${asn_code} | ASN 编号 |
| supplier | string | 是 | ${supplier_name} | 供应商 |
| goodsData | array[object] | 是 | [{"goods_code":"G0001","goods_actual_qty":10}] | 实际到货商品列表 |
| creater | string | 否 | api_auto_001 | 测试标识 |

**请求示例**

~~~json
{
  "asn_code": "${asn_code}",
  "supplier": "${supplier_name}",
  "goodsData": [
    {
      "goods_code": "${goods_code}",
      "goods_actual_qty": 10
    }
  ],
  "creater": "api_auto_${run_id}"
}
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "detail": "success"
}
~~~

- **断言要点：** detail 等于 success；主单和明细状态为 4；实到数量 10；pre_sort_stock 减 10，sorted_stock 加 10。

## 25、完成分拣失败—重复操作（ASN-SORTED-002）

#### 基本信息

- **Path：** /asn/sorted/{asn_id}/
- **Method：** POST
- **接口描述：** 对状态 4 ASN 再次提交分拣结果，验证状态机与库存幂等保护。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 是 | 登录返回的 user_id | 用于获取实际操作员工 |

**path**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_id | integer | 是 | ${asn_id} | 状态 4 ASN 的主键 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_code | string | 是 | ${asn_code} | ASN 编号 |
| supplier | string | 是 | ${supplier_name} | 供应商 |
| goodsData | array[object] | 是 | [{"goods_code":"G0001","goods_actual_qty":10}] | 重复提交相同实到数量 |

**请求示例**

~~~json
{
  "asn_code": "${asn_code}",
  "supplier": "${supplier_name}",
  "goodsData": [
    {
      "goods_code": "${goods_code}",
      "goods_actual_qty": 10
    }
  ]
}
~~~

#### 返回数据

- **响应状态码：** 200（当前源码异常处理缺陷）
- **响应数据：**

~~~json
{
  "detail": "This ASN Status Is Not 3",
  "status_code": 500
}
~~~

- **断言要点：** 响应体 status_code 等于 500；状态仍为 4；goods_actual_qty 和 sorted_stock 不得再次增加。

## 26、上架失败—数量为 0（ASN-MOVE-001）

#### 基本信息

- **Path：** /asn/movetobin/{detail_id}/
- **Method：** POST
- **接口描述：** 对状态 4 明细提交 0 件上架数量，验证数量边界。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 是 | 登录返回的 user_id | 用于获取实际操作员工 |

**path**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| detail_id | integer | 是 | ${detail_id} | 状态 4 ASN 明细主键 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_code | string | 是 | ${asn_code} | ASN 编号 |
| goods_code | string | 是 | ${goods_code} | 商品编码 |
| bin_name | string | 是 | ${bin_name} | Normal 库位 |
| qty | integer | 是 | 0 | 异常边界值 |

**请求示例**

~~~json
{
  "asn_code": "${asn_code}",
  "goods_code": "${goods_code}",
  "bin_name": "${bin_name}",
  "qty": 0
}
~~~

#### 返回数据

- **响应状态码：** 200（当前源码异常处理缺陷）
- **响应数据：**

~~~json
{
  "detail": "Move QTY Must > 0",
  "status_code": 500
}
~~~

- **断言要点：** 响应体 status_code 等于 500；sorted_qty 仍为 0；库存、stockbin 和数量变更记录不变化。

## 27、上架失败—数量超过实到数量（ASN-MOVE-002）

#### 基本信息

- **Path：** /asn/movetobin/{detail_id}/
- **Method：** POST
- **接口描述：** 实际到货 10 件时提交上架 11 件，验证超量拦截。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 是 | 登录返回的 user_id | 用于获取实际操作员工 |

**path**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| detail_id | integer | 是 | ${detail_id} | 状态 4 ASN 明细主键 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_code | string | 是 | ${asn_code} | ASN 编号 |
| goods_code | string | 是 | ${goods_code} | 商品编码 |
| bin_name | string | 是 | ${bin_name} | Normal 库位 |
| qty | integer | 是 | 11 | 大于实到数量 10 |

**请求示例**

~~~json
{
  "asn_code": "${asn_code}",
  "goods_code": "${goods_code}",
  "bin_name": "${bin_name}",
  "qty": 11
}
~~~

#### 返回数据

- **响应状态码：** 200（当前源码异常处理缺陷）
- **响应数据：**

~~~json
{
  "detail": "Move Qty must < Actual Arrive Qty",
  "status_code": 500
}
~~~

- **断言要点：** 响应体 status_code 等于 500；状态仍为 4；sorted_qty、库位库存、现有库存和可用库存均不变化。

## 28、全量上架成功（ASN-MOVE-003）

#### 基本信息

- **Path：** /asn/movetobin/{detail_id}/
- **Method：** POST
- **接口描述：** 将实际到货的 10 件商品全部上架到 Normal 库位，完成 ASN 入库。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 是 | 登录返回的 user_id | 用于获取实际操作员工 |

**path**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| detail_id | integer | 是 | ${detail_id} | 状态 4 ASN 明细主键 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| format | string | 否 | json | 响应格式 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| asn_code | string | 是 | ${asn_code} | ASN 编号 |
| goods_code | string | 是 | ${goods_code} | 商品编码 |
| bin_name | string | 是 | ${bin_name} | Normal 空库位 |
| qty | integer | 是 | 10 | 等于实际到货数量 |

**请求示例**

~~~json
{
  "asn_code": "${asn_code}",
  "goods_code": "${goods_code}",
  "bin_name": "${bin_name}",
  "qty": 10
}
~~~

#### 返回数据

- **响应状态码：** 200
- **响应数据：**

~~~json
{
  "detail": "success"
}
~~~

- **断言要点：** detail 等于 success；主单和明细状态为 5；sorted_stock 减 10；onhand_stock、can_order_stock 各加 10；库位由空变为非空。

## 29、查询并核对最终库存（ASN-STOCK-001）

#### 基本信息

- **Path：** /stock/list/；/stock/bin/
- **Method：** GET
- **接口描述：** 上架完成后分别查询商品总库存和库位库存，验证接口、数据库与业务增量一致。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 否 | 登录返回的 user_id | 框架可统一携带 |

**query**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| goods_code | string | 是 | ${goods_code} | 两个接口都使用 |
| bin_name | string | 库存库位接口是 | ${bin_name} | 仅 /stock/bin/ 使用 |
| page | integer | 否 | 1 | 页码 |
| max_page | integer | 否 | 20 | 每页数量 |
| format | string | 否 | json | 响应格式 |

**body**

无业务字段。POST 时发送空 JSON 对象 `{}`。

**请求示例**

~~~http
GET /stock/list/?goods_code=${goods_code}&page=1&max_page=20&format=json
GET /stock/bin/?goods_code=${goods_code}&bin_name=${bin_name}&page=1&max_page=20&format=json
~~~

#### 返回数据

- **响应状态码：** 200（两个接口）
- **响应数据：**

~~~json
{
  "stock_list_response": {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 301,
        "goods_code": "G0001",
        "goods_desc": "测试商品",
        "goods_qty": 10,
        "onhand_stock": 10,
        "can_order_stock": 10,
        "inspect_stock": 0,
        "hold_stock": 0,
        "damage_stock": 0,
        "asn_stock": 0,
        "dn_stock": 0,
        "pre_load_stock": 0,
        "pre_sort_stock": 0,
        "sorted_stock": 0,
        "pick_stock": 0,
        "picked_stock": 0,
        "back_order_stock": 0
      }
    ]
  },
  "stock_bin_response": {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 401,
        "bin_name": "A01-01-01",
        "goods_code": "G0001",
        "goods_desc": "测试商品",
        "goods_qty": 10,
        "pick_qty": 0,
        "picked_qty": 0,
        "bin_size": "Big",
        "bin_property": "Normal",
        "qty": 0,
        "t_code": "ab12..."
      }
    ]
  }
}
~~~

- **断言要点：** 中间阶段库存回到基线；onhand_stock 和 can_order_stock 均比基线增加 10；库位商品数量合计增加 10；接口值与数据库一致。

## 30、ASN 单商品完整入库链路（ASN-E2E-001）

#### 基本信息

- **Path：** 组合接口（/login/、主数据、/asn/*、/stock/*）
- **Method：** POST + GET
- **接口描述：** 一条 Allure 用例内串联登录、主数据、创建 ASN、添加明细、三段状态流转、上架和库存校验。

#### 请求参数

**headers**

| 参数名称 | 参数值 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| Content-Type | application/json | GET 可省略 | application/json | POST 接口建议保留 |
| Accept | application/json | 否 | application/json | 期望 JSON 响应 |
| token | ${token} | 是 | 登录返回的 openid | GreaterWMS 认证凭据 |
| operator | ${operator} | 是 | 登录返回的 user_id | 用于获取实际操作员工 |

**body**

| 参数名称 | 类型 | 是否必填 | 示例 | 备注 |
|---|---|---|---|---|
| ordered_qty | integer | 是 | 10 | 计划到货数量 |
| actual_qty | integer | 是 | 10 | 实际到货数量 |
| putaway_qty | integer | 是 | 10 | 上架数量 |
| run_id | string | 是 | 20260918_001 | 保证测试数据可追踪 |

**请求示例**

~~~json
[
  "1. POST /login/",
  "2. GET /supplier/、/goods/、/binset/、/stock/list/",
  "3. POST /asn/list/",
  "4. POST /asn/detail/",
  "5. GET /asn/detail/",
  "6. POST /asn/preload/{asn_id}/",
  "7. POST /asn/presort/{asn_id}/",
  "8. POST /asn/sorted/{asn_id}/",
  "9. POST /asn/movetobin/{detail_id}/",
  "10. GET /stock/list/、/stock/bin/"
]
~~~

#### 返回数据

- **响应状态码：** 每一步均为 200
- **响应数据：**

~~~json
{
  "final_result": "success",
  "asn_code": "${asn_code}",
  "asn_status": 5,
  "detail_status": 5,
  "goods_qty": 10,
  "goods_actual_qty": 10,
  "sorted_qty": 10,
  "stock_delta": {
    "goods_qty": 10,
    "onhand_stock": 10,
    "can_order_stock": 10,
    "asn_stock": 0,
    "pre_load_stock": 0,
    "pre_sort_stock": 0,
    "sorted_stock": 0
  }
}
~~~

- **断言要点：** 全部关联变量传递成功；状态按 1→2→3→4→5 流转；最终接口数据与数据库一致；本用例在 Allure 中只统计为 1 条。

## 附：实现时必须注意

1. 30 条是测试场景数，不代表 30 个唯一 URL。
2. 状态流转类用例不能依赖 pytest 执行顺序，应由 fixture 独立准备状态 1、2、3、4 的 ASN。
3. 反向用例除响应断言外，还应校验数据库未新增数据、库存未发生变化。
4. 完成上架后的 ASN 无法通过正常接口删除，建议使用专用测试数据库并在回归前恢复基线。
5. 后端异常处理器修复后，应把异常场景的外层 HTTP 断言改为实际 4xx/5xx。

