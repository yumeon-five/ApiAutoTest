# ------------------------------------------------------------
# 文件作用：Jenkins 交互模块，基于 python-jenkins 反向获取构建信息与测试报告统计。
# 核心操作：
#   1) 从 config.ini 读取 Jenkins 连接配置并建立连接；
#   2) 获取最新构建号、构建状态、控制台日志、job 描述与报告；
#   3) report_success_or_fail：统计通过/失败/跳过数、执行时长并提取报告链接，用于结果通知。
# ------------------------------------------------------------
import re

import jenkins
from conf.operationConfig import OperationConfig

conf = OperationConfig()
class OperJenkins(object):

    def __init__(self):
        # 读取 Jenkins 配置，timeout 做兜底，避免配置缺失时 int(None) 抛 TypeError
        timeout_val = conf.get_section_jenkins('timeout')
        try:
            timeout = int(timeout_val) if timeout_val is not None else 30
        except (TypeError, ValueError):
            timeout = 30

        self.__config = {
            'url': conf.get_section_jenkins('url'),
            'username': conf.get_section_jenkins('username'),
            'password': conf.get_section_jenkins('password'),
            'timeout': timeout,
        }
        self.__server = jenkins.Jenkins(**self.__config)

        self.job_name = conf.get_section_jenkins('job_name')

    def get_job_number(self):
        """读取jenkins job构建号"""
        build_number = self.__server.get_job_info(self.job_name).get('lastBuild').get('number')
        return build_number

    def get_build_job_status(self):
        """读取构建完成的状态"""
        build_num = self.get_job_number()
        job_status = self.__server.get_build_info(self.job_name, build_num).get('result')
        return job_status

    def get_console_log(self):
        """获取控制台日志"""
        console_log = self.__server.get_build_console_output(self.job_name, self.get_job_number())
        return console_log

    def get_job_description(self):
        """返回job描述信息"""
        description = self.__server.get_job_info(self.job_name).get('description')
        url = self.__server.get_job_info(self.job_name).get('url')

        return description, url

    def get_build_report(self):
        """返回第n次构建的测试报告"""
        report = self.__server.get_build_test_report(self.job_name, self.get_job_number())
        return report

    def report_success_or_fail(self):
        """统计测试报告用例成功数、失败数、跳过数以及成功率、失败率"""
        report_info = self.get_build_report()
        # 提取测试报告链接
        console_log = self.get_console_log()
        report_line = re.search(r'http://192.168.105.36:8088/job/hbjjapi/(.*?)allure', console_log).group(0)

        return report_line


if __name__ == '__main__':
    p = OperJenkins()
    res = p.report_success_or_fail()
    # result = re.search(r'http://192.168.105.36:8088/job/hbjjapi/(.*?)allure', res).group(0)
    print(res)
    # print(result)
