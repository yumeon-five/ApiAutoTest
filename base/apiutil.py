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
from common.connection import get_db_client
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
                # 注意：这里要找 "${" 而不能只找 "$"。
                # 断言里会写 JSONPath（not_null / gt 的值形如 $.count、$.data.openid），
                # 只找 "$" 会先命中 JSONPath 里的 $，把后面一大段内容当成占位符去解析，
                # 报错是 ValueError: substring not found（apiutil.py 里 index('(') 失败），
                # 完全看不出根因 —— 这个问题在「同一个用例里既有 ${} 关联又有 JSONPath 断言」时才会暴露。
                start_index = str_data.index("${")
                end_index = str_data.index("}", start_index)
                # 找到字符串的索引位置  ref_all_params: ${get_extract_data(product_id,1)}
                ref_all_params = str_data[start_index:end_index + 1]
                # 占位符只支持 ${函数名(参数)} 这种函数调用写法，写错了给一句能看懂的提示
                if '(' not in ref_all_params:
                    raise ValueError(f'yaml 里的占位符 {ref_all_params} 写法不支持，'
                                     f'只支持 ${{函数名(参数)}} 形式，例如 ${{get_extract_data(token)}}')
                # 取出函数名 func_name : get_extract_data
                func_name = ref_all_params[2:ref_all_params.index('(')]
                # 取出函数参数值 func_params product_id,1
                func_params = ref_all_params[ref_all_params.index('(') + 1:ref_all_params.index(')')]
                # 传入替换的参数获取对应的值
                extract_data = getattr(DebugTalk(), func_name)(*func_params.split(',') if func_params else "")
                # 将解析前的数值str_data替换解析后的数值extract_data
                # token: ${get_extract_data(product_id,1)} ---> "token": "123456"
                str_data = str_data.replace(ref_all_params, str(extract_data))

        # 还原数据：dict / list 都要还原成原类型。
        # 否则 validation（list）会被转成字符串，断言里遍历字符串会报
        # 'str' object has no attribute 'items'
        if isinstance(data, (dict, list)):
            data = json.loads(str_data)
        else:
            data = str_data
        return data

    def specification_yaml(self,base_info,test_case):
        """
        规范yaml接口测试数据的写法，后面可以在testcase直接调用方法
        :param base_info:yaml文件baseinfo数据
        :param test_case:yaml文件testcase数据
        :return:
        """
        cookie = None
        params_type = ['params', 'data', 'json']
        try:
            base_url = self.conf.get_envi('host')
            # URL 也走一遍 ${} 解析：链路用例的路径参数需要接口关联，
            # 例如 asn 各状态流转接口的地址是 /asn/preload/${get_extract_data(asn_id)}/，
            # 原来只对 header / 参数做替换，URL 里写 ${} 不会被解析
            url = self.replace_load(base_url + base_info['url'])
            allure.attach(url, f'接口地址:{url}')  # 测试报告中的测试步骤
            api_name = base_info['api_name']
            allure.attach(api_name, f'接口名称:{api_name}')
            method = base_info['method']
            allure.attach(method, f'请求方法:{method}')
            header = self.replace_load(base_info['header'])  # 解析请求头中的${}热加载
            allure.attach(str(header), f'请求头:{header}', allure.attachment_type.TEXT)
            try:
                cookie = self.replace_load(base_info['cookies'])  # 用动态解析的方法提取cookie值
                allure.attach(cookie, f'接口返回的cookie:{cookie}', allure.attachment_type.TEXT)
            except:
                pass
            # 必须 pop：一是 dict 不能像函数一样调用，二是若留在 test_case 里，
            # 下面 run_main(..., **test_case) 会重复传 case_name 导致 TypeError
            case_name = test_case.pop('case_name')
            allure.attach(case_name,f'测试用例名称:{case_name}',allure.attachment_type.TEXT)
            #处理cookies
            if base_info.get('cookies') is not None:
                cookie=eval(self.replace_load(base_info['cookies']))

            # 处理断言
            validation=self.replace_load(test_case.get('validation'))
            test_case['validation'] = validation
            test_case.pop('validation')
            #处理参数提取
            extract=test_case.pop('extract',None)
            extract_list=test_case.pop('extract_list',None)
            # 数据库基线快照：必须在发请求之前查库并落盘，供「增量断言」比对（见 snapshot_db）
            db_before=test_case.pop('db_before',None)
            #处理接口的请求参数
            for key, value in test_case.items():
                if key in params_type:
                    test_case[key] = self.replace_load(value)
            #处理文件上传接口
            file,files=test_case.pop('files', None), None
            if file is not None:
                for fk,fv in file.items():
                    allure.attach(json.dumps(file),'导入文件')
                    files={fk:open(fv,mode='rb')}

            # 发请求之前先做数据库基线快照（放在这里：既在请求之前，又能用到上面已经解析过的 extract.yaml）
            if db_before is not None:
                self.snapshot_db(db_before)

            res = self.send.run_main(name=api_name, url=url, case_name=case_name, method=method, header=header,
                                     cookies=cookie, file=files, **test_case)
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

    def snapshot_db(self, snapshot_cases):
        """
        执行数据库查询并把结果写入 extract.yaml，作为「增量断言」的基线（发请求之前执行）。

        为什么需要：有些字段只能断言「变化量」而不能断言绝对值。
        比如库存 stocklist.goods_qty —— 加一次明细它就涨一次，同一套用例跑第二遍，
        绝对值的期望就过期了；而且同一个商品在库里可能有多行库存记录，更没法写死。
        有了基线，断言就可以写成「本次执行后 - 执行前 == 预期增量」。

        yaml 写法（testCase 里和 json / validation 同级）：
            db_before:
              stock_snapshot:                 # 基线名，validation 里的 delta_from 用它引用
                sql: "select goods_qty, asn_stock from stocklist where goods_code = ?"
                params: ["A00001"]

        写入 extract.yaml 的是查询结果的第一行（dict）；查不到数据时写 None（表示"本来就没有这条数据"）。
        """
        for key, db_case in snapshot_cases.items():
            db_case = self.replace_load(db_case)
            rows = get_db_client().query(db_case.get('sql'), db_case.get('params'))
            baseline = rows[0] if rows else None
            logs.info(f'数据库基线快照 {key}：{baseline}')
            allure.attach(str(baseline), f'数据库基线快照:{key}', allure.attachment_type.TEXT)
            self.read.write_yaml_data({key: baseline})

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
