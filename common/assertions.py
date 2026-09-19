import json
import operator

import allure
import jsonpath

from common.connection import get_db_client
from common.recordlog import logs

class Assertions:
    """
    接口断言模式封装，支持：
    1.字符串包含
    2.结果相等断言
    3.结果不相等断言
    4.断言接口返回值里面的任意一个值
    5.数据库断言
    6.字段存在且非空断言（not_null）
    7.字段不存在断言（not_exists，负向断言）
    8.数值大于断言（gt）
    """

    def _get_by_jsonpath(self,response,expression):
        """
        按 JSONPath 从响应里取值，返回 (是否取到, 值) 二元组。

        为什么要单独封装：jsonpath.jsonpath() 匹配不到时返回的是布尔值 False，
        取到 JSON null 时返回的是 [None]——两者要区分开，
        否则「字段不存在」和「字段存在但值为 null」会给出同样的错误提示。

        实测：
            jsonpath.jsonpath({'data': {'password': None}}, '$.data.password') -> [None]
            jsonpath.jsonpath({'data': {}}, '$.data.openid')                   -> False
        """
        try:
            result = jsonpath.jsonpath(response, expression)
        except Exception as e:
            logs.error(f'JSONPath 表达式解析失败：{expression}，原因：{e}')
            return False, None
        # False 表示没匹配到；不是 list 或空 list 也视为没取到
        if result is False or not isinstance(result, list) or len(result) == 0:
            return False, None
        return True, result[0]

    def contains_assert(self,value,response,status_code):
        """
        第一种模式:字符串包含断言，断言预期结果的字符串是否包含在接口的实际返回的结果
        :param value:预期结果，yaml文件当中validation关键字下的结果
        :param response:
        :param status_code:
        :return:
        """
        # 断言状态标识，0代表成功，其他代表失败
        flag = 0
        for assert_key,assert_value in value.items():
            if assert_key =='status_code':
                if assert_value != status_code:
                    flag+=1
                    allure.attach(f'预期结果为:{assert_value}\n实际结果为:{status_code}','响应代码断言结果:失败',allure.attachment_type.TEXT)
                    logs.error('contanis断言失败，接口返回【%s】不等于【%s】'%(status_code,assert_value))
            else:
                resp_list=jsonpath.jsonpath(response,'$..%s' %assert_key)
                # 修复：字段不存在时 jsonpath 返回 False，原来直接取 resp_list[0] 会抛
                # TypeError: 'bool' object is not subscriptable，把「断言失败」变成「用例报错」。
                # 这里改为明确判定为断言失败，并记录可读的失败原因。
                if resp_list is False or not resp_list:
                    flag+=1
                    logs.error(f'响应断言结果:失败!响应中不存在字段:{assert_key}，预期结果为:{assert_value}')
                    allure.attach(f'预期字段:{assert_key}\n预期结果:{assert_value}\n实际结果:响应中不存在该字段',
                                  '响应文本断言结果:失败',allure.attachment_type.TEXT)
                    continue
                if isinstance(resp_list[0],str) and isinstance(assert_value,str):
                    resp_list=','.join(resp_list)
                    if assert_value in resp_list:
                        logs.info(f'字符串断言成功!预期结果为:{assert_value}\n,实际结果为:{resp_list}')
                    else:
                        flag+=1
                        logs.error(f'响应断言结果:失败!预期结果为:{assert_value}\n,实际结果为:{resp_list}')
                        allure.attach(f'预期结果为:{assert_value}\n实际结果为:{resp_list}', '响应文本断言结果:失败',
                                      allure.attachment_type.TEXT)
                else:
                    # 修复：非字符串字段（数字 / 布尔 / 字典等）没有「子串包含」的语义，
                    # 原来只判断 isinstance(resp_list[0], str)，遇到数字字段会一个分支都不进——
                    # 既不记日志也不累加 flag，等于「静默通过」。
                    # 这类字段退化成相等比较：只要有一个匹配值等于预期值就算通过。
                    if any(item == assert_value for item in resp_list):
                        logs.info(f'字段值断言成功!预期结果为:{assert_value},实际结果为:{resp_list}')
                    else:
                        flag+=1
                        logs.error(f'响应断言结果:失败!预期结果为:{assert_value},实际结果为:{resp_list}')
                        allure.attach(f'预期结果为:{assert_value}\n实际结果为:{resp_list}','字段值断言结果:失败',
                                      allure.attachment_type.TEXT)

        return flag

    def equal_assert(self,value,response):
        """
        2.结果相等断言模式（子集比较）

        :param value:预期结果，也就是yaml文件里面的validation关键字下的参数 dict类型
        :param response:接口的实际返回结果  dict类型
        :return:flag标识，0表示测试通过，非0表示测试不通过

        修复了两个问题：
        1）原来只支持「单个字段」的相等断言：它用 list(value.keys())[0] 取第一个 key，
           把响应里其它 key 全删掉再整体比较，所以写
           `eq: {'code': '200', 'msg': 'Success Create'}` 必然失败（响应已被删成只剩 code）。
           现在改成：只比较 expected 里写出来的字段，写几个比几个。
        2）原来用 `del response[rl]` 就地修改了传入的响应字典，
           同一个用例里 eq 后面再写 contains/rv 断言，拿到的会是被截断的响应。
           现在只读不写，response 在整个用例的断言过程中保持不变。
        """
        flag=0
        if not (isinstance(value,dict) and isinstance(response,dict)):
            raise TypeError('相等断言失败--类型错误,预期结果和接口的实际响应结果必须为字典类型！')

        # 只从实际响应里摘出「预期结果声明过的字段」，形成子集
        actual_subset={}
        missing_keys=[]
        for key in value:
            if key in response:
                actual_subset[key]=response[key]
            else:
                missing_keys.append(key)

        if missing_keys:
            flag+=1
            logs.error(f'相等断言失败:响应中不存在预期字段:{missing_keys}，实际响应:{response}')
            allure.attach(f'预期结果:{str(value)}\n实际结果:响应中不存在字段{missing_keys}\n完整响应:{json.dumps(response,ensure_ascii=False)}',
                          '相等断言结果:失败',allure.attachment_type.TEXT)
            return flag

        if operator.eq(actual_subset,value):
            logs.info(f'相等断言成功:接口的实际结果为:{actual_subset}，等于预期结果:{str(value)}')
        else:
            flag=flag+1
            logs.error(f'相等断言失败:接口的实际结果为:{actual_subset}，不等于预期结果:{str(value)}')
            allure.attach(f'预期结果:{str(value)}\n实际结果:{str(actual_subset)}','相等断言结果:失败',
                          allure.attachment_type.TEXT)
        return flag

    def not_null_assert(self,expressions,response):
        """
        6.字段存在且非空断言

        :param expressions:JSONPath 表达式列表，例如 ['$.data.openid', '$.data.user_id']
                           也可以只写一个字符串 '$.data.openid'
        :param response:接口的实际返回结果 dict
        :return:flag标识，0表示测试通过

        为什么需要它：原有的 contains 断言对空字符串恒为真（'' in '任意字符串' 永远是 True），
        rv 断言只能和固定值做相等比较——两者都表达不了「字段存在且非空」这个最常见的断言要求。
        """
        flag=0
        # 兼容只写一个 JSONPath 字符串的写法，统一转成 list 处理
        if isinstance(expressions,str):
            expressions=[expressions]

        for expression in expressions:
            exists,value=self._get_by_jsonpath(response,expression)
            if not exists:
                flag+=1
                logs.error(f'存在性断言失败:[{expression}] 在响应中取不到对应的字段')
                allure.attach(f'JSONPath:{expression}\n实际结果:字段不存在\n完整响应:{json.dumps(response,ensure_ascii=False)}',
                              '字段存在且非空断言:失败',allure.attachment_type.TEXT)
            elif value is None or value == '' or value == [] or value == {}:
                # 字段取到了，但值是空的（null / 空字符串 / 空列表 / 空字典）同样判定失败
                flag+=1
                logs.error(f'存在性断言失败:[{expression}] 取到的值为空 -> {value!r}')
                allure.attach(f'JSONPath:{expression}\n实际结果:字段值为空 {value!r}',
                              '字段存在且非空断言:失败',allure.attachment_type.TEXT)
            else:
                logs.info(f'存在性断言成功:[{expression}] -> {value!r}')
        return flag

    def not_exists_assert(self,expressions,response):
        """
        7.字段不存在断言（负向断言）

        :param expressions:JSONPath 表达式列表，例如 ['$.data.openid']
        :param response:接口的实际返回结果 dict
        :return:flag标识，0表示测试通过

        典型用途：登录失败、鉴权失败时断言「响应里不能出现 openid / token」，
        这类负向断言在安全回归里最容易被漏掉。
        """
        flag=0
        if isinstance(expressions,str):
            expressions=[expressions]

        for expression in expressions:
            exists,value=self._get_by_jsonpath(response,expression)
            if exists:
                flag+=1
                logs.error(f'不存在断言失败:[{expression}] 不应该出现，实际取到的值为 {value!r}')
                allure.attach(f'JSONPath:{expression}\n实际结果:字段存在且值为 {value!r}\n完整响应:{json.dumps(response,ensure_ascii=False)}',
                              '字段不存在断言:失败',allure.attachment_type.TEXT)
            else:
                logs.info(f'不存在断言成功:[{expression}] 未在响应中出现')
        return flag

    def gt_assert(self,value,response):
        """
        8.数值大于断言

        :param value:字典，key 是 JSONPath，value 是阈值，例如 {'$.data.user_id': 0}
        :param response:接口的实际返回结果 dict
        :return:flag标识，0表示测试通过

        典型用途：登录成功后断言 data.user_id（staff 表主键）为正整数。
        """
        flag=0
        for expression,expected in value.items():
            exists,actual=self._get_by_jsonpath(response,expression)
            # bool 是 int 的子类，需要单独排除，避免 True 被当成 1 通过断言
            if not exists or isinstance(actual,bool) or not isinstance(actual,(int,float)):
                flag+=1
                logs.error(f'数值断言失败:[{expression}] 期望是数字且大于 {expected}，实际取到:{actual!r}(字段不存在或类型不是数字)')
                allure.attach(f'JSONPath:{expression}\n预期:大于 {expected} 的数字\n实际:{actual!r}',
                              '数值比较断言:失败',allure.attachment_type.TEXT)
            elif actual <= expected:
                flag+=1
                logs.error(f'数值断言失败:[{expression}] 期望大于 {expected}，实际为 {actual}')
                allure.attach(f'JSONPath:{expression}\n预期:大于 {expected}\n实际:{actual}',
                              '数值比较断言:失败',allure.attachment_type.TEXT)
            else:
                logs.info(f'数值断言成功:[{expression}] {actual} > {expected}')
        return flag

    def not_equal_assert(self,expected_results,actual_results):
        """
        3.不相等断言模式
        :param expected_results: 预期结果，yaml文件validation值
        :param actual_results: 接口实际响应结果
        :return:
        """
        flag = 0
        if isinstance(actual_results, dict) and isinstance(expected_results, dict):
            # 找出实际结果与预期结果共同的key
            common_keys = list(expected_results.keys() & actual_results.keys())[0]
            # 根据相同的key去实际结果中获取，并重新生成一个实际结果的字典
            new_actual_results = {common_keys: actual_results[common_keys]}
            eq_assert = operator.ne(new_actual_results, expected_results)
            if eq_assert:
                logs.info(f"不相等断言成功：接口实际结果：{new_actual_results}，不等于预期结果：" + str(expected_results))
                allure.attach(f"预期结果：{str(expected_results)}\n实际结果：{new_actual_results}", '不相等断言结果：成功',
                              attachment_type=allure.attachment_type.TEXT)
            else:
                flag += 1
                logs.error(f"不相等断言失败：接口实际结果{new_actual_results}，等于预期结果：" + str(expected_results))
                allure.attach(f"预期结果：{str(expected_results)}\n实际结果：{new_actual_results}", '不相等断言结果：失败',
                              attachment_type=allure.attachment_type.TEXT)
        else:
            raise TypeError('不相等断言--类型错误，预期结果和接口实际响应结果必须为字典类型！')
        return flag

    def assert_response_any(self, actual_results, expected_results):
        """
        4.断言接口响应信息中的body的任何属性值
        :param actual_results: 接口实际响应信息
        :param expected_results: 预期结果，在接口返回值的任意值
        :return: 返回标识,0表示测试通过，非0则测试失败
        """
        flag = 0
        try:
            exp_key = list(expected_results.keys())[0]
            if exp_key in actual_results:
                act_value = actual_results[exp_key]
                rv_assert = operator.eq(act_value, list(expected_results.values())[0])
                if rv_assert:
                    logs.info("响应结果任意值断言成功")
                else:
                    flag += 1
                    logs.error("响应结果任意值断言失败")
        except Exception as e:
            logs.error(e)
            raise
        return flag
    def assert_db(self,db_case):
        """
        5.数据库断言：执行 SQL，并把查询结果与期望值比对
        （拿库里的真实数据和接口返回值做交叉验证，纯接口断言做不到这类判定）

        yaml 写法（validation 里的一条）：
            - db:
                sql: "select asn_code, bar_code from asnlist where asn_code = ?"
                params: ["${get_extract_data(asn_code)}"]   # 可选，占位符用 ?（参数化，不拼字符串）
                rows: 1                                      # 可选，期望命中的行数
                expect:                                      # 可选，期望的字段值（取第一行比对）
                  asn_code: "${get_extract_data(asn_code)}"
                  bar_code: "${get_extract_data(bar_code)}"
                                                                 负向断言示例（库里不应新增记录）：
            - db:
                sql: "select count(*) as cnt from asnlist where creater = ?"
                params: ["api_auto_${get_run_id()}"]
                expect: {cnt: 1}

        :param db_case: dict，必须包含 sql；rows / expect 至少要有一个，否则这条断言没有任何判定依据
        :return: flag 标识，0 表示通过，非 0 表示失败

        说明：原来的实现（assert_mysql）只判断「查询结果不是 None」，
        空结果集（[]）也会被判为通过 —— 等于只要有张表、SQL 不报错就算过，
        做不了「库里的值 = 接口返回的值」这种校验，所以这里重写。
        """
        flag = 0
        if not isinstance(db_case, dict) or not db_case.get('sql'):
            raise AssertionError(f'db 断言写法错误，至少要写 sql：{db_case}')

        sql = db_case['sql']
        params = db_case.get('params')
        expect_rows = db_case.get('rows')
        expect_fields = db_case.get('expect')

        if expect_rows is None and not expect_fields:
            raise AssertionError(f'db 断言必须至少写 rows 或 expect 之一，否则没有判定依据：{db_case}')

        conn = get_db_client()
        rows = conn.query(sql, params)
        if rows is None:
            flag += 1
            logs.error(f'数据库断言失败：SQL 执行失败或数据库未连通。SQL={sql}，参数={params}')
            allure.attach(f'SQL:{sql}\n参数:{params}\n实际结果:查询失败',
                          '数据库断言结果:失败', allure.attachment_type.TEXT)
            return flag

        logs.info(f'数据库断言 SQL：{sql}，参数：{params} -> 命中 {len(rows)} 行：{rows}')

        # 1) 行数断言
        if expect_rows is not None and len(rows) != expect_rows:
            flag += 1
            logs.error(f'数据库断言失败：期望命中 {expect_rows} 行，实际 {len(rows)} 行')
            allure.attach(f'SQL:{sql}\n参数:{params}\n预期行数:{expect_rows}\n实际行数:{len(rows)}\n实际结果:{rows}',
                          '数据库断言结果:失败', allure.attachment_type.TEXT)

        # 2) 字段值断言（取第一行比对）
        if expect_fields:
            if not rows:
                flag += 1
                logs.error(f'数据库断言失败：期望的字段值无从比对，查询结果为空。{expect_fields}')
                allure.attach(f'SQL:{sql}\n参数:{params}\n预期字段值:{expect_fields}\n实际结果:查询结果为空',
                              '数据库断言结果:失败', allure.attachment_type.TEXT)
            else:
                actual_row = rows[0]
                mismatch = {}
                for field, expect_value in expect_fields.items():
                    actual_value = actual_row.get(field)
                    if actual_value != expect_value:
                        mismatch[field] = {'预期': expect_value, '实际': actual_value}
                if mismatch:
                    flag += 1
                    logs.error(f'数据库断言失败：字段值与预期不一致 {mismatch}')
                    allure.attach(f'SQL:{sql}\n参数:{params}\n不一致字段:{mismatch}\n实际行:{actual_row}',
                                  '数据库断言结果:失败', allure.attachment_type.TEXT)
                else:
                    logs.info(f'数据库字段值断言成功：{expect_fields}')

        if flag == 0:
            logs.info('数据库断言通过')
        return flag

    def assert_result(self,expected,response,status_code):
        """
        断言模式,通过all_flag标记
        :param expected:预期结果
        :param response:接口的实际返回结果 json格式
        :param status_code:接口的实际返回状态码
        :return:

        修复的坑：原来遇到不认识的断言关键字（例如把 eq 拼成 eqq）时，
        只在日志里打一句「不支持此种断言方式」就继续往下走，
        all_flag 仍然是 0，最后 assert True —— 用例全绿但一条断言都没执行。
        现在改为：未知关键字、validation 缺失/为空，都直接判定用例失败。
        """
        all_flag=0
        # 支持的关键字列表，新增断言模式时要同步维护这里
        supported_keys=('contains','eq','ne','rv','db','not_null','not_exists','gt')
        unknown_keys=[]
        # validation 没写或者写成空列表时，用例实际上没有任何校验，不能算通过
        # 注意：这个判断放在 try 外面，报错信息才不会被下面的 except 包装成「接口断言异常」
        if not expected:
            raise AssertionError('validation 未配置或为空，该用例没有任何断言，不允许判定为通过')
        try:
            logs.info("yaml文件预期结果：%s" % expected)
            for expected_result in expected:
                for key, value in expected_result.items():
                    if key == "contains":
                        flag = self.contains_assert(value, response, status_code)
                        all_flag = all_flag + flag
                    elif key == "eq":
                        flag = self.equal_assert(value, response)
                        all_flag = all_flag + flag
                    elif key == 'ne':
                        flag = self.not_equal_assert(value, response)
                        all_flag = all_flag + flag
                    elif key == 'rv':
                        flag = self.assert_response_any(actual_results=response, expected_results=value)
                        all_flag = all_flag + flag
                    elif key == 'db':
                        flag = self.assert_db(value)
                        all_flag = all_flag + flag
                    elif key == 'not_null':
                        flag = self.not_null_assert(value, response)
                        all_flag = all_flag + flag
                    elif key == 'not_exists':
                        flag = self.not_exists_assert(value, response)
                        all_flag = all_flag + flag
                    elif key == 'gt':
                        flag = self.gt_assert(value, response)
                        all_flag = all_flag + flag
                    else:
                        # 记录未知关键字，循环结束后统一失败，避免「静默通过」
                        unknown_keys.append(key)
                        logs.error("不支持此种断言方式:%s" % key)

        except Exception as exceptions:
            logs.error('接口断言异常，请检查yaml预期结果值是否正确填写!')
            raise exceptions

        if unknown_keys:
            assert False, (f'validation 中出现了不支持的断言关键字:{unknown_keys}，'
                           f'当前支持:{list(supported_keys)}；请检查是否拼写错误')

        if all_flag == 0:
            logs.info("测试成功")
            assert True
        else:
            logs.error("测试失败")
            assert False





