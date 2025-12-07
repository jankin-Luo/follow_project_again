import logging, os
import time
from pathlib import Path
from logging.handlers import RotatingFileHandler

from conf import setting

log_path = setting.FILE_PATH['LOG']
if not os.path.exists(log_path):
    os.mkdir(log_path)
# print(log_path)

logfile_name = Path(log_path) / 'test.{}.log'.format(time.strftime('%Y%m%d%H%M%S'))
print(logfile_name)


class RecordLog:
    '''封装log日志'''

    def output_logging(self):
        '''获取logger对象'''
        logger = logging.getLogger(__name__)
        # 防止打印重复log日志
        if not logger.handlers:
            logger.setLevel(setting.LOG_LEVEL)
            log_format = logging.Formatter(
                "%(asctime)s - %(filename)s:%(lineno)d - [%(module)s:%(funcName)s] - %(name)s - %(levelname)s - %(message)s"
            )
            # 日志输出到指定文件,（文件保存形式）
            fh = RotatingFileHandler(filename=logfile_name,  # 日志文件名
                                     maxBytes=1024 * 1024 * 10,  # 每个日志文件最大大小（10MB）
                                     backupCount=3,  # 保留的旧日志文件数量
                                     mode='a',
                                     encoding='utf-8')
            fh.setLevel(setting.LOG_LEVEL)
            fh.setFormatter(log_format)
            # 再将相应的handler添加到logger中
            logger.addHandler(fh)

            # 输出日志到控制台
            sh = logging.StreamHandler()
            sh.setLevel(setting.STREAM_LOG_LEVEL)
            sh.setFormatter(log_format)

            logger.addHandler(sh)

        return logger


apilog = RecordLog()
logs = apilog.output_logging()
