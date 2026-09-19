import pytest
import time
import requests
from common.recordlog import logs
from common.readyaml import ReadYamlData
from common.feishu import send_fs_msg
from common.operJenkins import OperJenkins
from conf.operationConfig import OperationConfig

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


