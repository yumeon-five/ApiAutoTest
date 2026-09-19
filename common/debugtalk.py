"""
4.实现yaml文件的功能，接口参数加密 MD5
"""
import random
import time

from common.readyaml import ReadYamlData



class DebugTalk(object):
    # 类属性：同一次运行内所有 DebugTalk 实例共享。
    # 因为 base/apiutil.py 的 replace_load 每次都是 getattr(DebugTalk(), func_name) 新建实例，
    # 用实例属性存不住，必须放在类属性上。
    _run_id = None

    def __init__(self):
        self.read = ReadYamlData()

    def get_run_id(self):
        """
        返回本次运行的唯一标识（格式 yyyyMMddHHmmss），yaml 里用 ${get_run_id()} 调用。

        用途：构造可追溯的测试数据。比如创建入库单时把 creater 写成 api_auto_${get_run_id()}，
        跑完能一眼看出这条数据是哪一次自动化跑出来的，也方便清理。

        注意：同一次运行内多次调用返回同一个值（首次调用时生成），
        这样「请求参数里的取值」和「validation 里的预期值」才能对得上。
        """
        if DebugTalk._run_id is None:
            DebugTalk._run_id = time.strftime('%Y%m%d%H%M%S')
        return DebugTalk._run_id

    def get_extract_order_data(self,data,randoms):
        """
        按照排序顺序读取数据,不加0，-1，-2的情况
        """
        if randoms not in [0,-1,-2]:
            return data[randoms - 1]

    def get_extract_data(self,node_name,sec_node_name=None,randoms=None):
        """
        获取extract.yaml的数据 提取返回值数据
        :param node_name: extract.yaml中的key值
        :param randoms: 随机读取extract.yaml的数据
        :return:
        """
        data = self.read.get_extract_yaml(node_name)
        return data

    def get_extract_data_list(self,node_name,randoms=None):
        """
        获取extract.yaml文件的数据
        :param node_name:
        :param randoms:
        :return:
        """
        data=self.read.get_extract_yaml(node_name)
        if randoms is not None:
            randoms=int(randoms)
            data_value={
                randoms : 1,
                0 : random.choice(data),
                -1 : ','.join(data),
                -2 : ','.join(data).split(',')
            }
            data=data_value[randoms]
        return data


    def Md5_params(self,params):
        """实现MD5加密"""
        return 'ABCDEFGHIJK'+str(params)

if __name__ == '__main__':
    debugtalk = DebugTalk()
    print(debugtalk.get_extract_data('product_id',1))