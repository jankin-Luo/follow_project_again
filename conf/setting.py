import os, sys, logging

DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(DIR_PATH)

# log日志输出级别
LOG_LEVEL = logging.DEBUG #日志输出到文件级别
STREAM_LOG_LEVEL = logging.DEBUG  #日志输出到控制台


#文件路径
FILE_PATH = {
    'extract' : os.path.join(DIR_PATH,'extract.yaml'),
    'conf': os.path.join(DIR_PATH, 'conf', 'config.ini'),
    'LOG': os.path.join(DIR_PATH,'log')
}

print(FILE_PATH['conf'])