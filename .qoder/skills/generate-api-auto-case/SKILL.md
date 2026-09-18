---
name: generate-api-auto-case
description: 根据接口文档/需求文档批量生成结构化的接口测试用例文档，产出「每个接口一个 Markdown 用例文件 + 一个按 interface_key 分 Sheet 的汇总 Excel」。当用户需要基于接口文档生成接口测试用例、测试用例文档、测试点、用例表格，或提到「生成测试用例 / 接口用例 / apicase」时使用。
---

# 生成接口测试用例（generate-api-auto-case）

你是一位资深测试开发工程师，负责把接口文档（Markdown）转换为高质量、可执行的接口测试用例。
本技能**不内联**具体规范，所有规则统一引用同目录 `reference/` 下的三份文档；Excel 由 `scripts/gen_excel.py` 生成。

## 规范文档（生成前必须先读）

| 文档 | 作用 |
| ---- | ---- |
| [reference/testcase-spec.md](reference/testcase-spec.md) | 测试点设计规范：设计方法、场景覆盖、优先级 P0–P3、用例编号（`uuid.uuid4().hex`）、断言规范、动态占位符 `{{ 变量名 }}` |
| [reference/apicase-template.md](reference/apicase-template.md) | 单个接口 Markdown 用例文件的结构模板 |
| [reference/apicase-template-excel.md](reference/apicase-template-excel.md) | 汇总 Excel 的列格式说明（与 `gen_excel.py` 输出严格一致） |

**冲突裁决**：三份文档若有不一致，一律以 `testcase-spec.md` 为准（用例编号用 32 位 hex、URL 用 `{{ URL }}`、优先级用 P0–P3）。

## 工作流程

复制以下清单并逐项推进：

```
- [ ] 步骤1：确认目标路径（接口文档所在文件夹，读取其中全部 .md）
- [ ] 步骤2：解析接口信息 + 识别公共模块 / 独立模块
- [ ] 步骤3：为每个接口设计用例，产出中间数据 cases.json
- [ ] 步骤4：运行 scripts/gen_excel.py 生成 .xlsx 与 接口_index.json
- [ ] 步骤5：按 apicase-template.md 为每个接口生成 <接口名>_测试用例.md
```

**步骤1 · 确认目标路径**
向用户确认接口文档所在目录，读取该目录下所有 `.md`。缺少必要信息（参数类型、是否必填等）时主动澄清。

**步骤2 · 解析与模块识别**
逐个接口提取：接口名、请求方法、URL/路径、请求头、URL 参数、请求体参数、响应结构、业务规则、断言要点。
- **公共模块**：出现在 ≥2 个页面/接口的功能（如登录鉴权、分页查询、统一异常）。抽到独立接口条目集中管理。
- **独立模块**：仅属于单一接口的功能。
- 若未识别到公共模块，对应文件/章节填写「无」。

**步骤3 · 设计用例并产出中间 JSON**
按 `testcase-spec.md` 的设计方法（等价类、边界值、因果、场景法）为每个接口设计正常/异常/边界用例，写入 `cases.json`（格式见下）。`case_id` 可留空，交由脚本补全。

**步骤4 · 生成 Excel**
运行 `scripts/gen_excel.py`，产出汇总 `.xlsx` 与 `接口_index.json`（含每个接口最终的 `case_id`）。

**步骤5 · 生成 Markdown**
按 `apicase-template.md` 为每个接口生成 `<接口名>_测试用例.md`，其中 `用例编号` 必须取自 `接口_index.json`，保证与 Excel 完全一致。

## 输出目录结构

所有产物写入 `{项目名称}/02-测试/接口测试用例/`（`{项目名称}` 从路径或对话推断，无法确定时询问用户）：

```
{项目名称}/02-测试/接口测试用例/
├── <接口名>_测试用例.md      # 步骤5：每个接口一个 Markdown 用例文件
├── cases.json               # 步骤3：中间数据，gen_excel.py 的输入
├── 接口_index.json           # 步骤4：接口→用例编号索引（脚本生成）
└── <项目名>.xlsx             # 步骤4：汇总 Excel，每接口一个 Sheet（脚本生成）
```

## 中间 JSON 数据格式（cases.json）

`cases.json` 是「Agent 设计用例」与「gen_excel.py 生成 Excel」之间的唯一契约。
`interfaces` 为**字典**，键即 `interface_key`，天然实现「按 interface_key 分组、每接口一个 Sheet」。

```json
{
  "project_name": "用户中心项目",
  "output_xlsx": "用户中心项目.xlsx",
  "interfaces": {
    "loginUser": {
      "interface_name": "登录接口",
      "sheet_name": "登录接口",
      "cases": [
        {
          "case_id": "",
          "title": "登录接口-正确账号密码登录",
          "precondition": "数据库存在账号 {{ 正确账号 }} / 密码 {{ 正确密码 }}",
          "priority": "P0",
          "url": "{{ URL }}/api/login",
          "method": "POST",
          "headers": "Content-Type: application/json\nAuthorization: {{ 有效Token }}",
          "query_params": "无",
          "body_params": "{\"username\":\"{{ 正确账号 }}\",\"password\":\"{{ 正确密码 }}\"}",
          "expected": "响应状态码：200\n响应格式：JSON\ncode 等于 0\nmsg 包含\"成功\"\ndata.token 存在且非空"
        }
      ]
    }
  }
}
```

字段说明：

| 字段 | 层级 | 必填 | 说明 |
| ---- | ---- | ---- | ---- |
| `project_name` | 根 | 否 | 项目名称，仅用于记录 |
| `output_xlsx` | 根 | 否 | 输出 Excel 文件名/相对路径；缺省用 `cases.xlsx` |
| `interfaces` | 根 | 是 | 字典，键为 `interface_key`（分组依据） |
| `interface_name` | 接口 | 否 | 接口中文名，用于 Sheet 名与 MD 标题 |
| `sheet_name` | 接口 | 否 | 指定 Sheet 名；缺省依次取 `interface_name`→`interface_key` |
| `cases` | 接口 | 是 | 该接口的用例数组 |
| `case_id` | 用例 | 否 | 留空则脚本用 `uuid.uuid4().hex` 补全（32 位无横杠） |
| `title` | 用例 | 是 | `接口名-场景名称` |
| `precondition` | 用例 | 是 | 前置条件，无则填「无」 |
| `priority` | 用例 | 是 | `P0`/`P1`/`P2`/`P3` |
| `url` | 用例 | 是 | `{{ URL }}{{ 路径 }}` 格式 |
| `method` | 用例 | 是 | `GET`/`POST`/`PUT`/`DELETE` 等 |
| `headers` | 用例 | 是 | `参数名: 值`，多个用 `\n` 分隔；无则填「无」 |
| `query_params` | 用例 | 是 | `参数名: 值`，多个用 `\n`；无则填「无」 |
| `body_params` | 用例 | 是 | JSON 字符串或 `参数名: 值`；无则填「无」 |
| `expected` | 用例 | 是 | 多行断言，用 `\n` 分隔；含响应状态码、响应格式、业务断言 |

> 字段命名与 Excel 列一一对应，详见 `reference/apicase-template-excel.md`。

## 生成 Excel（scripts/gen_excel.py）

**Excel 规则**：每个接口单独一个 Sheet，依据 `interface_key` 分组区分；Sheet 名取 `sheet_name`→`interface_name`→`interface_key`，自动清洗为 Excel 合法（去除 `[]:*?/\`）、≤31 字符且不重复的名称。缺失的 `case_id` 由脚本用 `uuid.uuid4().hex` 补全，并写入 `接口_index.json`。

**依赖**：`openpyxl`（缺失时脚本会提示 `pip install openpyxl`）。

**执行命令**（在项目根目录 `d:/projects/auto-test` 下）：

```bash
# 基本用法：输出 xlsx 与 接口_index.json 到 cases.json 同目录
python .qoder/skills/generate-api-auto-case/scripts/gen_excel.py "{项目名称}/02-测试/接口测试用例/cases.json"

# 指定输出 Excel 路径
python .qoder/skills/generate-api-auto-case/scripts/gen_excel.py path/to/cases.json -o path/to/用户中心项目.xlsx

# 指定接口索引输出路径
python .qoder/skills/generate-api-auto-case/scripts/gen_excel.py path/to/cases.json --index path/to/接口_index.json
```

脚本执行后打印：生成的 Excel 路径、Sheet 数（接口数）、用例总数、接口索引路径。
随后从 `接口_index.json` 读取每个接口的 `caseIds`（顺序与 `cases` 一致），用于步骤5 回填 Markdown 的 `用例编号`。

## 关键约束（务必遵守）

- **用例编号**：`uuid.uuid4().hex`，32 位无横杠；禁止 `TC_{模块}_{序号}`。由脚本统一生成，MD 与 Excel 必须一致。
- **动态数据占位符**：账号、密码、Token、ID、手机号、分页值等一律用 Jinja2 风格 `{{ 变量名 }}`，禁止写死真实值。
- **断言**：用自然语言描述，必要时补 JSONPath 或正则；禁止把完整 JSON 响应体当作预期结果。
- **空节点**：无请求头/URL 参数/请求体时，Markdown 保留对应表格标题并预留空行，Excel/JSON 填「无」，不得删除整节。
