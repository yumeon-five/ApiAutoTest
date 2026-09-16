import os
import sys
import logging

DIR_PATH=os.path.dirname(os.path.dirname(__file__))
sys.path.append(DIR_PATH)

#log日志的输出级别
LOG_LEVEL = logging.DEBUG  #日志输出到文件的级别
STREAM_LEVEL = logging. DEBUG  #输出日志到控制台

#文件路径
FILE_PATH={
    'extract': os.path.join(DIR_PATH, 'extract.yaml'),
    'conf': os.path.join(DIR_PATH, 'conf','conf.ini'),
    'log': os.path.join(DIR_PATH, 'log')
}

