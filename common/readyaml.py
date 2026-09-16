"""
3.获取yaml文件数据，写入yaml文件数据
"""
import os
import yaml
from conf.setting import FILE_PATH


def get_testcase_yaml(file):
    """
    获取yaml文件的数据
    :param file:yaml文件的路径
    :return:
    """
    try:
        with open(file,'r',encoding='UTF-8') as f:
            yaml_data = yaml.safe_load(f)
            return yaml_data
    except Exception as e:
        print(e)

class ReadYamlData(object):
    """读取yaml数据，以及写入数据到yaml文件"""
    def __init__(self,yaml_file=None):
        if yaml_file is not None:
            self.yaml_file = yaml_file
        else:
            self.yaml_file = '../testcase/login/login.yaml'
    def write_yaml_data(self,value):
        """
        写入数据到yaml文件
        :param value: (dict)写入的数据
        :return:
        """
        file=None
        file_path= FILE_PATH['extract']
        if not os.path.exists(file_path):
            os.system(file_path)
        try:
            file=open(file_path,'a',encoding='utf-8')
            if isinstance(value,dict):
                write_data=yaml.dump(value,allow_unicode=True,sort_keys=False)
                file.write(write_data)
            else:
                print('写入【extract.yaml】文件的格式为字典类型')
        except Exception as e:
            print(e)
        finally:
            file.close()

    def get_extract_yaml(self,node_name):
        """
        读取接口提取的变量值
        :param node_name:yaml文件的key值
        :return:
        """
        file_path= FILE_PATH['extract']
        if os.path.exists(file_path):
            pass
        else:
            print("extract.yaml文件不存在")
            with open(file_path, 'w', encoding='utf-8'):
                pass
            print('extract.yaml文件创建成功!')
        with open(file_path, 'r', encoding='utf-8') as f:
            extract_data=yaml.safe_load(f) or {}
            return extract_data[node_name]

    def clear_yaml_data(self):
        """清空extract.yaml文件的内容，目的：重新写入覆盖之前的内容，防止占用空间"""
        with open(FILE_PATH['extract'], 'w', encoding='utf-8') as f:
            f.truncate()

if __name__ == '__main__':
    # SendRequest 仅演示代码使用，放在此处导入，避免与 sendrequests 循环导入
    from common.sendrequests import SendRequest
    res=get_testcase_yaml('../testcase/login/login.yaml')[0]
    url=res['baseInfo']['url']
    new_url='http://127.0.0.1:8787'+url
    method=res['baseInfo']['method']
    data=res['testCase'][0]['data']


    sendrequest = SendRequest()
    res = sendrequest.run_main(url=new_url,data=data,header=None,method=method)
    # print(res)

    # token = res.get('token')
    # write_data={}
    # write_data['Token']=token
    # read=ReadYamlData()
    # read.write_yaml_data(write_data)

    read=ReadYamlData()
    print(read.get_extract_yaml('Token'))