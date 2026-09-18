# Excel 列格式说明（汇总 .xlsx）

汇总 Excel 由 `scripts/gen_excel.py` 依据中间数据 `cases.json` 生成。本文档定义列格式，与脚本输出严格一致。生成规范见 `testcase-spec.md`，Markdown 结构见 `apicase-template.md`。

## Sheet 规则

- **每个接口单独一个 Sheet**，依据 `interface_key` 分组区分（`cases.json::interfaces` 的每个键对应一个 Sheet）。
- Sheet 名优先取 `sheet_name`，其次 `interface_name`，最后 `interface_key`。
- Sheet 名自动清洗：去除非法字符 `[ ] : * ? / \`，长度截断至 ≤31 字符，重名时追加 `_1`、`_2` 后缀保证唯一。
- 每个 Sheet 第 1 行为表头（冻结），从第 2 行起每行一条用例。

## 列定义

列顺序、表头名称、来源字段与 `cases.json` 的映射如下（脚本按此顺序写列）：

| 序号 | 列名（表头） | cases.json 字段 | 说明 | 示例 |
| :--- | :----------- | :-------------- | :--- | :--- |
| 1 | 接口Key | `interface_key`（分组键） | 关联接口唯一标识 | `loginUser` |
| 2 | 用例编号 | `case_id` | 32 位 hex，留空由脚本用 `uuid.uuid4().hex` 补全 | `a1b2c3d4e5f647899abcdef012345678` |
| 3 | 测试标题 | `title` | 接口名-场景名称 | `登录接口-正确账号密码登录` |
| 4 | 前置条件 | `precondition` | 执行前需满足的条件，无则填「无」 | `数据库存在账号 {{ 正确账号 }}` |
| 5 | 优先级 | `priority` | P0 / P1 / P2 / P3 | `P0` |
| 6 | 请求URL | `url` | `{{ URL }}{{ 路径 }}`，可用占位符 | `{{ URL }}/api/login` |
| 7 | 请求方法 | `method` | GET / POST / PUT / DELETE 等 | `POST` |
| 8 | 请求头 | `headers` | `参数名: 值`，多个用换行分隔，无则「无」 | `Content-Type: application/json`（换行）`Authorization: {{ 有效Token }}` |
| 9 | URL参数 | `query_params` | `参数名: 值`，多个换行，无则「无」 | `userId: {{ 用户ID }}`（换行）`page: 1` |
| 10 | 请求体参数 | `body_params` | JSON 字符串或 `参数名: 值`，无则「无」 | `{"username":"{{ 正确账号 }}","password":"{{ 正确密码 }}"}` |
| 11 | 预期结果 | `expected` | 响应状态码 + 响应格式 + 业务断言，多条换行 | `响应状态码：200`（换行）`响应格式：JSON`（换行）`code 等于 0`（换行）`data.token 存在且非空` |

> 单元格内的「换行」在 `cases.json` 中用 `\n` 表示；脚本写入时开启自动换行。

## 示例行（Excel 中的一行数据）

| 接口Key | 用例编号 | 测试标题 | 前置条件 | 优先级 | 请求URL | 请求方法 | 请求头 | URL参数 | 请求体参数 | 预期结果 |
| :------ | :------- | :------- | :------- | :----- | :------ | :------- | :----- | :------ | :--------- | :------- |
| loginUser | a1b2c3d4e5f647899abcdef012345678 | 登录接口-正确账号密码登录 | 数据库存在账号 {{ 正确账号 }} / 密码 {{ 正确密码 }} | P0 | {{ URL }}/api/login | POST | Content-Type: application/json | 无 | {"username":"{{ 正确账号 }}","password":"{{ 正确密码 }}"} | 响应状态码：200 / 响应格式：JSON / code 等于 0 / data.token 存在且非空 |

## 配套产物：接口_index.json

脚本在生成 Excel 的同时输出 `接口_index.json`，记录每个接口最终的用例编号，供 Markdown 回填：

```json
{
  "interfaces": {
    "loginUser": {
      "interface_name": "登录接口",
      "caseIds": ["a1b2c3d4e5f647899abcdef012345678", "..."]
    }
  }
}
```

`caseIds` 顺序与 `cases.json::interfaces[key].cases` 一致；Markdown 的 `用例编号` 必须取自此处。
