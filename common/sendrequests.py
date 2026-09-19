"""
2.封装接口请求方法 GET POST
"""
import json

import allure
import pytest

from common.readyaml import ReadYamlData
from common.recordlog import logs

import requests

class SendRequest(object):
    """
    封装接口的请求
    """
    def __init__(self):
        self.read=ReadYamlData()


    #**kwargs字典类型传参
    def send_request(self,**kwargs):
        """
        封装发送接口请求方法
        :param kwargs:
        :return:
        """
        cookie={}
        session = requests.session()
        result=None
        # HTTP 头部的值必须是字符串。yaml 里用 ${} 关联出来的值可能是数字
        # （比如 operator 是登录返回的 data.user_id = 81），
        # 不转换的话 requests 会抛 InvalidHeader: Header part (81) ... must be of type str or bytes。
        # 注意只转「头」，请求体（json）和 SQL 参数不转，那里保留原生类型才有意义。
        if kwargs.get('headers'):
            kwargs['headers'] = {k: str(v) for k, v in kwargs['headers'].items()}
        try:
            result=session.request(**kwargs)
            set_cookie=requests.utils.dict_from_cookiejar(result.cookies)
            if set_cookie:
                cookie['Cookie']=set_cookie
                self.read.write_yaml_data(set_cookie)
                logs.info(f'cookie:{cookie}')
            logs.info(f'接口的实际返回信息:{result.text if result.text else result}')
        except requests.exceptions.ConnectionError:
            logs.error('接口连接服务器异常!')
            pytest.fail('接口请求异常，可能是request的连接数过多或者请求速度过快导致程序报错！')
        except requests.exceptions.HTTPError:
            logs.error('HTTP异常!')
            pytest.fail('HTTP请求异常！')
        except requests.exceptions.RequestException as e:
            logs.error(e)
            pytest.fail('请求异常，请检查系统或数据是否正常！')
        return result

    def run_main(self,name,url,case_name,header,method,cookies=None,file=None,**kwargs):
        """
        发送接口请求
        :param name:
        :param url:
        :param case_name:
        :param header:
        :param method:
        :param cookies:
        :param file:
        :param kwargs:
        :return:
        """
        try:
            #收集报告日志信息
            logs.info(f'接口名称:{name}')
            logs.info(f'接口请求地址:{url}')
            logs.info(f'接口请求方法:{method}')
            logs.info(f'接口测试用例名称:{case_name}')
            logs.info(f'接口请求头:{header}')
            logs.info(f'Cookie:{cookies}')
            #处理请求参数
            req_params=json.dumps(kwargs,ensure_ascii=False)
            if 'data' in kwargs.keys():
                logs.info(f'接口请求参数:{kwargs}')
                allure.attach(req_params, f'请求参数:{req_params}', allure.attachment_type.TEXT)
            elif 'json' in kwargs.keys():
                logs.info(f'接口请求参数:{kwargs}')
                allure.attach(req_params, f'请求参数:{req_params}', allure.attachment_type.TEXT)
            elif 'params' in kwargs.keys():
                logs.info(f'接口请求参数:{kwargs}')
                allure.attach(req_params, f'请求参数:{req_params}', allure.attachment_type.TEXT)
        except Exception as e:
            logs.error(e)
        response=self.send_request(method=method,url=url,headers=header,cookies=cookies,files=file,verify=False,**kwargs)
        return response


if __name__ == '__main__':
    url = 'http://127.0.0.1:8008/dar/user/login'
    data = {
        "user_name": "test01",
        "passwd": "admin123"
    }
    method = "post"
    header = None
    sendrequest = SendRequest()
    res = sendrequest.run_main(url,data,header,method)
    print(res)





