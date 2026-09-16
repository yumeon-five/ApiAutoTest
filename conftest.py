import pytest
from common.recordlog import logs
from common.readyaml import ReadYamlData


read=ReadYamlData()
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

