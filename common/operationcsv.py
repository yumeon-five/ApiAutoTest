
import csv
import os.path

from common.recordlog import logs
from conf.setting import DIR_PATH


def read_csv(file_name):
    """
    :param file_name: csv文件名
    :return:
    """
    try:
        with open(os.path.join(DIR_PATH,'data',file_name),'r',encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            for value in csv_reader:
                print(value)
            return csv_reader

    except Exception as e:
        logs.error(e)
if __name__ == '__main__':
    read_csv('login_data.csv')