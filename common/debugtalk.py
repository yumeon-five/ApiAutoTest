"""
4.实现yaml文件的功能，接口参数加密 MD5
"""
import random

from common.readyaml import ReadYamlData



class DebugTalk(object):
    def __init__(self):
        self.read = ReadYamlData()

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