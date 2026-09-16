"""用来读取配置文件"""
import configparser
from conf.setting import FILE_PATH

class OperationConfig:
    """封装读取conf.ini配置文件"""

    def __init__(self,file_path=None):

        if file_path is None:
            self.__file_path=FILE_PATH['conf']
        else:
            self.__file_path=file_path
        self.conf=configparser.ConfigParser()
        try:
            self.conf.read(self.__file_path,encoding='utf-8')
        except Exception as e:
            print(e)

    def get_section_for_data(self,section,option):
        """
        读取conf.ini数据文件
        :param section:conf.ini的头部值 例子:[api_envi]
        :param option:选项值的key  例子：host
        :return:
        """
        try:
            data=self.conf.get(section,option)
            return data
        except Exception as e:
            print(e)

    def get_envi(self,option):
        """获取接口服务器的ip地址"""
        return self.get_section_for_data('api_envi',option)

    def get_mysql_conf(self,option):
        """获取接口服务器ip地址"""
        return self.get_section_for_data('MYSQL',option)

if __name__ == '__main__':
    oper=OperationConfig()
    print(oper.get_section_for_data('api_envi', 'host'))
    print(oper.get_envi('host'))