import pytest
import time
from common.recordlog import logs
from common.readyaml import ReadYamlData
from common.feishu import send_fs_msg


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

    content=  f"""
    自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：
    测试用例总数：{case_total}
    测试通过数：{passed}
    测试失败数：{failed}
    错误数量：{error}
    跳过执行数量：{skipped}
    执行总时长：{duration}
    点击查看测试报告：
    """
    send_fs_msg(content)


