import os
import pytest
import time
import requests
from common.recordlog import logs
from common.readyaml import ReadYamlData
from common.clean_data import clean_asn_by_api
from common.feishu import send_fs_msg
from common.operJenkins import OperJenkins
from conf.operationConfig import OperationConfig
from conf.setting import FILE_PATH

read=ReadYamlData()

# 自己记录会话开始时间，避免依赖 pytest 内部属性（不同版本类型不一致：float/Instant）
_SESSION_START_TIME = time.time()


def pytest_sessionstart(session):
    """pytest 会话开始时触发，记录开始时间戳"""
    global _SESSION_START_TIME
    _SESSION_START_TIME = time.time()


@pytest.fixture(scope='session', autouse=True)
def clear_extract_data():
    """前置操作：清除extract.yaml文件中的数据"""
    read.clear_yaml_data()


@pytest.fixture(scope='session', autouse=True)
def login_first(clear_extract_data):
    """
    业务线前置：会话开始先登录一次，把 token / operator 写入 extract.yaml。

    用户管理、商品管理、ASN 入库等模块的用例里写了 ${get_extract_data(token)} 做接口关联，
    而 clear_extract_data 每次会话都会清空 extract.yaml，因此必须先登录拿凭证；
    否则 get_extract_data('token') 会抛 KeyError: 'token'。
    显式依赖 clear_extract_data，保证「先清空、再登录」的顺序。

    写入的两个变量（对应 WMS 的两个请求头，见 GreaterWMS/utils/auth.py 和 asn/views.py）：
      token    -> data.openid，DRF 接口读 HTTP_TOKEN
      operator -> data.user_id（staff 表主键），写操作接口读 HTTP_OPERATOR

    修复记录：
    1) 原来请求的是 /dar/user/login + form 参数 user_name/passwd，那是另一个项目的接口，
       WMS 实际是 /login/ + JSON 参数 name/password，导致每次运行都报
       「前置登录异常：Expecting value: line 1 column 1 (char 0)」（404 返回 HTML，res.json() 解析失败）。
    2) 原来失败只 log.error 不抛异常，属于静默失败：依赖 token 的模块会在后面
       以 KeyError: 'token' 这种毫不相干的报错挂掉。现在改为 pytest.fail 快速失败，
       让问题在会话最开头就暴露出来。
    """
    # 前置检查：conf/conf.ini 是本地环境配置，不入库，新环境 clone 后要先从模板复制一份。
    # 缺文件时 configparser 不会抛异常（read 会静默忽略不存在的文件），只会让 host 读成 None，
    # 最后表现成 "Invalid URL 'None/login/'" 这种看不出根因的报错，所以在这里提前拦一下。
    if not os.path.exists(FILE_PATH['conf']):
        pytest.fail(f'配置文件不存在：{FILE_PATH["conf"]}\n'
                    f'请复制 conf/conf.ini.example 为 conf/conf.ini，并按实际环境填写。')

    config = OperationConfig()
    host = config.get_envi('host')
    # 账号密码统一放在 conf/conf.ini 的 [LOGIN] 段，代码里不再硬编码
    username = config.get_login_conf('username')
    password = config.get_login_conf('password')
    url = f'{host}/login/'
    try:
        res = requests.post(url, json={'name': username, 'password': password}, timeout=10)
    except Exception as e:
        pytest.fail(f'前置登录请求异常：{url} -> {e}')

    # 接口返回非 JSON（404 页面 / 500 错误页）时，给出能直接定位问题的报错，
    # 而不是让 res.json() 抛 JSONDecodeError 这种看不出根因的异常
    try:
        res_json = res.json()
    except ValueError:
        pytest.fail(f'前置登录返回的不是 JSON，请确认接口地址与后端服务是否正常：{url}\n'
                    f'HTTP {res.status_code}\n响应内容：{res.text[:500]}')

    data = res_json.get('data') or {}
    token = data.get('openid')
    operator = data.get('user_id')
    if str(res_json.get('code')) != '200' or not token or not operator:
        pytest.fail(f'前置登录失败：url={url}，账号={username}\n'
                    f'响应={res_json}\n'
                    f'（请检查 conf/conf.ini 的 [LOGIN] 账号是否存在、密码是否正确）')

    read.write_yaml_data({'token': token, 'operator': operator})
    logs.info(f'前置登录成功，token / operator 已写入 extract.yaml：{token} / {operator}')


@pytest.fixture(scope='session', autouse=True)
def clean_history_data(login_first):
    """
    会话开始前清理上一次运行遗留的自动化测试数据。

    为什么需要：创建入库单这类写接口每跑一次就造一条数据，不做清理的话
    列表查询的 count / results 会被历史数据干扰（也看不到"本次运行造了哪些数据"），
    测试库还会越跑越大。清理按 creater 前缀识别测试数据（用例里写成 api_auto_${get_run_id()}），
    不会碰手工造的数据。

    依赖 login_first：清理要带着 token 调接口，所以必须排在登录之后。
    清理失败只记 warning 不抛异常 —— 它属于收尾工作，不该因为清理出问题就让整个会话跑不起来。

    开关和前缀在 conf/conf.ini 的 [CLEAN] 段配置。
    """
    config = OperationConfig()
    if str(config.get_clean_conf('enable')) != '1':
        logs.info('测试数据清理未开启（[CLEAN] enable != 1），跳过')
        return

    prefix = config.get_clean_conf('creater_prefix') or 'api_auto'
    try:
        summary = clean_asn_by_api(creater_prefix=prefix)
        logs.info(f'测试数据清理完成：前缀“{prefix}”匹配到 {summary["found"]} 条，'
                  f'已删除 {summary["deleted"]} 条，跳过 {summary["skipped"]} 条')
        for detail in summary['details']:
            logs.info(f'  清理明细：{detail}')
    except Exception as e:
        logs.warning(f'测试数据清理失败，跳过（不影响用例执行）：{e}')


def pytest_collection_modifyitems(config, items):
    """
    按测试模块声明的 CHAIN_ORDER 排序，保证「链路用例」按业务顺序执行。

    为什么需要：pytest 默认按文件名排序执行，但文件名排序不等于业务顺序。
    ASN 入库链路是 创建(1) -> 明细 -> 预装车(2) -> 预分拣(3) -> 完成分拣(4) -> 上架(5)，
    光按文件名排出来的是 create / detail / list / movetobin / preload / presort / sorted —— 顺序是乱的，
    而每一步都依赖上一步改完的状态，跑错顺序就会一路报 "This ASN Status Is Not X"。

    用法：在测试模块顶部声明链路序号，例如 test_asn_preload.py 里写 CHAIN_ORDER = 30。
    没声明的模块取默认值 1000（排在最后）；sort 是稳定排序，同序号的模块保持原有相对顺序。
    """
    def chain_order(item):
        module = getattr(item, 'module', None)
        return getattr(module, 'CHAIN_ORDER', 1000)

    items.sort(key=chain_order)


@pytest.fixture(scope='session',autouse=True)
def fixture_test():
    """前后置处理"""
    logs.info('----------------------接口测试开始---------------------')
    yield
    logs.info('----------------------接口测试结束---------------------')

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    pytest内置的钩子函数，函数名为固定写法，不可以变更
    每次pytest测试完成后，会自动收集测试结果的数据
    :param terminalreporter: 内部终端报告对象，对象的stats属性
    :param exitstatus:将报告返回操作系统的退出状态
    :param config:pytest配置对象
    :return:
    """
    print(terminalreporter.stats)
    #收集测试用例总数
    case_total = terminalreporter._numcollected
    print(f'测试用例总数:{case_total}')
    #收集测试用例通过数
    passed=len(terminalreporter.stats.get('passed',[]))
    print(f'测试用例通过数:{passed}')
    # 收集测试用例失败数
    failed=len(terminalreporter.stats.get('failed',[]))
    print(f'测试用例失败数:{failed}')
    #收集测试用例错误数
    error=len(terminalreporter.stats.get('error',[]))
    print(f'测试用例错误数:{error}')
    #收集测试用例跳过数
    skipped=len(terminalreporter.stats.get('skipped',[]))
    print(f'测试用例跳过数:{skipped}')
    duration = time.time() - _SESSION_START_TIME
    print(f'测试用例执行时常:{duration:.2f}s')
    # Jenkins / 飞书属于外部通知服务，失败时不应影响 pytest 收尾
    try:
        oper = OperJenkins()
        report = oper.report_success_or_fail()
    except Exception as e:
        logs.warning(f'获取 Jenkins 测试报告失败，跳过通知：{e}')
        report = '获取失败'
        return
    content = f"""
    自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：
    测试用例总数：{case_total}
    测试通过数：{passed}
    测试失败数：{failed}
    错误数量：{error}
    跳过执行数量：{skipped}
    执行总时长：{duration}
    点击查看测试报告：{report}
    """
    try:
        send_fs_msg(content)
    except Exception as e:
        logs.warning(f'发送飞书通知失败：{e}')


