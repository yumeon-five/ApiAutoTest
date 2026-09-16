"""
接口的工具 封装操作方法
"""
import json
import re
import allure
import jsonpath

from common.debugtalk import DebugTalk
from common.readyaml import ReadYamlData
from common.readyaml import get_testcase_yaml
from common.recordlog import logs
from common.sendrequests import SendRequest
from common.assertions import Assertions
from conf.operationConfig import OperationConfig

assert_res = Assertions()

class BaseRequest(object):

    def __init__(self):
        self.send = SendRequest()
        self.conf = OperationConfig()
        self.read = ReadYamlData()


    def replace_load(self, data):
        """
        解析替换yaml文件中${}的数据
        解析yaml文件的数据  例子：${get_extract_data(token)}
        """
        str_data = data
        if not isinstance(data, str):
            # 如果不是字符串类型，就会转成字符串类型
            str_data = json.dumps(data, ensure_ascii=False)

        for i in range(str_data.count('${')):
            if "${" in str_data and "}" in str_data:
                # index检测是否含有${字符，并且找到字符串的索引位置
                start_index = str_data.index("$")
                end_index = str_data.index("}", start_index)
                # 找到字符串的索引位置  ref_all_params: ${get_extract_data(product_id,1)}
                ref_all_params = str_data[start_index:end_index + 1]
                # 取出函数名 func_name : get_extract_data
                func_name = ref_all_params[2:ref_all_params.index('(')]
                # 取出函数参数值 func_params product_id,1
                func_params = ref_all_params[ref_all_params.index('(') + 1:ref_all_params.index(')')]
                # 传入替换的参数获取对应的值
                extract_data = getattr(DebugTalk(), func_name)(*func_params.split(',') if func_params else "")
                # 将解析前的数值str_data替换解析后的数值extract_data
                # token: ${get_extract_data(product_id,1)} ---> "token": "123456"
                str_data = str_data.replace(ref_all_params, str(extract_data))

        # 还原数据
        if data and isinstance(data, dict):
            data = json.loads(str_data)
        else:
            data = str_data
        return data

    def specification_yaml(self, case_info):
        """
        规范yaml接口测试数据的写法，后面可以在testcase直接调用方法
        :param case_info:list类型
        :return:
        """
        cookie = None
        params_type = ['params', 'data', 'json']
        try:
            base_url = self.conf.get_envi('host')
            url = base_url + case_info['baseInfo']['url']
            allure.attach(url, f'接口地址:{url}')  # 测试报告中的测试步骤
            api_name = case_info['baseInfo']['api_name']
            allure.attach(api_name, f'接口名称:{api_name}')
            method = case_info['baseInfo']['method']
            allure.attach(method, f'请求方法:{method}')
            header = self.replace_load(case_info['baseInfo']['header'])  # 解析请求头中的${}热加载
            allure.attach(str(header), f'请求头:{header}', allure.attachment_type.TEXT)
            try:
                cookie = self.replace_load(case_info['baseInfo']['cookies'])  # 用动态解析的方法提取cookie值
                allure.attach(cookie, f'接口返回的cookie:{cookie}', allure.attachment_type.TEXT)
            except:
                pass
            for tc in case_info['testCase']:
                case_name = tc.pop('case_name')  # 提取case_name字段信息
                allure.attach(case_name, f'测试用例名称:{case_name}')
                validation = tc.pop('validation')
                extract = tc.pop('extract', None)  # 没有这个参数就返回None
                extract_list = tc.pop('extract_list', None)
                # print(tc)    #提取其他信息仅保留了  {'data': {'user_name': 'test02', 'passwd': 'abc123'}}
                for key, value in tc.items():
                    if key in params_type:
                        tc[key] = self.replace_load(value)
                res = self.send.run_main(name=api_name, url=url, case_name=case_name, method=method, header=header,
                                         cookies=cookie, file=None, **tc)
                allure.attach(res.text, f'接口的响应信息:{res.text}', allure.attachment_type.TEXT)
                res_text = res.text
                res_json = res.json()
                if extract is not None:
                    self.extract_data(extract, res_text)
                if extract_list is not None:
                    self.extract_data_list(extract_list, res_text)
                #处理接口断言
                assert_res.assert_result(validation, res_json,res.status_code)
        except Exception as e:
            logs.error(e)
            raise e

    def extract_data(self, testcase_extract, response):
        """
        提取接口的返回值，支持正则表达式提取以及json提取。
        :param testcase_extract:yaml文件中extract的值
        :param response:接口的实际返回值
        :return:
        """
        pattenr_list = ['(.+?)', '(.*?)', r'(\d+)', r'(\d*)']
        try:
            for key, value in testcase_extract.items():
                # 处理正则表达式的提取
                for pat in pattenr_list:
                    if pat in value:
                        ext_list = re.search(value, response)
                        print(ext_list)
                        if pat in [r'(\d+)', r'(\d*)']:
                            extract_data = {key: int(ext_list.group(1))}
                        else:
                            extract_data = {key: ext_list.group(1)}
                        logs.info(f'正则表达式提取的参数:{extract_data}')
                        allure.attach(str(extract_data), f'正则提取的参数:{key}', allure.attachment_type.TEXT)
                        self.read.write_yaml_data(extract_data)
                if "$" in value:
                    ext_json = jsonpath.jsonpath(json.loads(response), value)[0]
                    if ext_json:
                        extract_data = {key: ext_json}
                    else:
                        extract_data = {key: '未提取到数据，该接口返回值为空或者json提取表达式有误！'}
                    logs.info(f'json提取到的参数:{extract_data}')
                    allure.attach(str(extract_data), f'json提取的参数:{key}', allure.attachment_type.TEXT)
                    self.read.write_yaml_data(extract_data)
        except Exception as e:
            logs.error('接口返回值提取异常，请检查yaml文件的extract表达式是否正确！')

    def extract_data_list(self, testcase_extract_list, response):
        """
        提取多个参数，支持正则表达式和json提取，提取结果以列表形式返回
        :param testcase_extract_list: yaml文件中的extract_list信息
        :param response: 接口的实际返回值,str类型
        :return:
        """
        try:
            for key, value in testcase_extract_list.items():
                if "(.+?)" in value or "(.*?)" in value:
                    ext_list = re.findall(value, response, re.S)
                    if ext_list:
                        extract_date = {key: ext_list}
                        logs.info('正则提取到的参数：%s' % extract_date)
                        allure.attach(str(extract_date), f'正则提取的参数:{key}', allure.attachment_type.TEXT)
                        self.read.write_yaml_data(extract_date)
                if "$" in value:
                    # 增加提取判断，有些返回结果为空提取不到，给一个默认值
                    ext_json = jsonpath.jsonpath(json.loads(response), value)
                    if ext_json:
                        extract_date = {key: ext_json}
                    else:
                        extract_date = {key: "未提取到数据，该接口返回结果可能为空"}
                    logs.info('json提取到参数：%s' % extract_date)
                    allure.attach(str(extract_date), f'json提取的参数:{key}', allure.attachment_type.TEXT)
                    self.read.write_yaml_data(extract_date)
        except:
            logs.error('接口返回值提取异常，请检查yaml文件extract_list表达式是否正确！')


if __name__ == '__main__':
    res = BaseRequest()
    data = get_testcase_yaml('../testcase/login/login.yaml')[0]
    print(res.specification_yaml(data))
