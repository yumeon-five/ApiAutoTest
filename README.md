基于 Python + Pytest + Requests + YAML + JSONPath + SQLite + Allure + Jenkins 搭建的接口自动化测试项目，覆盖入库单，从创建到上架、库存核对的完整业务链路。

项目重点不只是“发送接口请求”，而是验证一条真实仓储业务链路中的：
登录鉴权与接口关联；

ASN 状态流转；

响应结果与数据库数据一致性；

库存阶段性变化与最终增量；

Jenkins 持续集成与 Allure 测试报告。

本项目仅用于学习和测试实践，请在独立测试环境中运行。

项目亮点

YAML 数据驱动：接口信息、请求参数、提取规则和断言规则与测试代码分离。

动态参数关联：使用 JSONPath 提取 token、operator、asn_id、asn_code、detail_id 等变量，供后续接口引用。

原生类型保留：占位符替换后保留整数、列表、字典等 JSON 类型，避免字符串与数字比较失败。

多层断言：支持 HTTP 状态码、响应字段、JSONPath 非空/不存在、数值比较和数据库断言。

数据库增量校验：请求前保存库存基线，请求后校验库存变化量，而不是依赖容易失效的固定值。

完整状态链路：验证 ASN 状态严格按照 1 → 2 → 3 → 4 → 5 流转。

双层用例设计：既有按接口拆分的回归用例，也有一条包含 15 个步骤的完整 E2E 冒烟用例。

测试报告与持续集成：Pytest 生成 Allure 原始结果，Jenkins 负责拉取代码、执行回归和发布报告。

核心业务流程

    A[登录并获取凭证] --> B[查询供应商、商品和空库位]
    B --> C[记录商品与库位库存基线]
    C --> D[创建 ASN 主单：状态 1]
    D --> E[添加商品明细：状态 1]
    E --> F[预装车：1 → 2]
    F --> G[预分拣：2 → 3]
    G --> H[完成分拣：3 → 4]
    H --> I[商品上架：4 → 5]
    I --> J[核对主单、明细及库存增量]

完整 E2E 链路包含以下 15 个步骤：

登录并提取认证信息；

查询可用供应商；

查询可用商品；

查询 Normal 空库位；

保存总库存和库位库存基线；

创建 ASN 主单；

添加 ASN 商品明细；

预装车；

预分拣；

完成分拣；

查询明细并提取 detail_id；

商品上架；

按 ID 查询 ASN 主单；

核对商品总库存增量；

核对库位库存增量。

框架架构

flowchart TD
    A[YAML 测试数据] --> B[readyaml.py：读取与展开]
    B --> C[test_*.py：Pytest 参数化]
    C --> D[apiutil.py：占位符解析与流程编排]
    D --> E[sendrequests.py：统一请求发送]
    E --> F[GreaterWMS API]
    F --> G[apiutil.py：JSONPath 参数提取]
    G --> H[extract.yaml：运行时变量池]
    H --> D
    F --> I[assertions.py：响应断言]
    I --> J[connection.py：数据库一致性与增量断言]
    C --> K[Allure 原始结果]
    L[conftest.py：登录、清理、排序、Hook] --> C
    M[Jenkins] --> C
    K --> M

一条用例的执行过程

读取 YAML
  → 解析 ${函数名(参数)} 占位符
  → 发送 HTTP 请求
  → 提取响应参数并保存
  → 执行响应断言
  → 执行数据库断言
  → 生成 Allure 测试结果

目录结构

ApiAutoTest/
├─ base/
│  └─ apiutil.py                 # YAML 规范解析、参数替换、提取和流程编排
├─ common/
│  ├─ assertions.py              # 响应断言、JSONPath 断言、数据库断言
│  ├─ clean_data.py              # 测试数据清理
│  ├─ connection.py              # SQLite / MySQL / Redis 连接封装
│  ├─ debugtalk.py               # YAML 动态函数及运行时数据方法
│  ├─ readyaml.py                # YAML 读取及运行时变量管理
│  ├─ recordlog.py               # 日志封装
│  └─ sendrequests.py            # Requests 请求封装
├─ conf/
│  ├─ conf.ini.example           # 无敏感信息的配置模板
│  ├─ operationConfig.py         # 配置读取
│  └─ setting.py                 # 公共路径及日志级别
├─ testcase/
│  ├─ login/                     # 登录接口 YAML 与 Pytest 用例
│  └─ asn/                       # ASN 入库链路 YAML 与 Pytest 用例
├─ 接口测试用例/                  # 接口测试用例文档及 Excel
├─ conftest.py                   # Fixture、执行顺序和 Pytest Hook
├─ pytest.ini                    # Pytest 与 Allure 配置
├─ requirements.txt              # Python 依赖
└─ run.py                        # 本地执行入口

用例覆盖

当前共收集 34 条 Pytest 用例，覆盖成功、异常、鉴权、幂等和数据库一致性场景。

模块

用例数

主要验证内容

登录鉴权

4

登录成功、密码错误、缺少密码、异常输入

基础数据查询

4

供应商、商品、库位、库存基线

创建 ASN

4

创建成功、参数异常、创建后查询

添加商品明细

5

成功、数量异常、重复/无效数据、库存变化

预装车

2

状态 1 → 2、重复操作拦截

预分拣

2

状态 2 → 3、错误状态拦截

完成分拣

2

状态 3 → 4、重复提交拦截

查询明细

2

查询成功、不存在的 ASN

商品上架

3

数量为 0、超量、成功上架

最终数据核对

3

主单状态、总库存、库位库存

完整 E2E

1

登录到库存核对的 15 步链路

ASN 列表与鉴权

2

有 Token 查询、无 Token 拦截

合计

34

