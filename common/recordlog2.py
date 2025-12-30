import logging,os
import time
from pathlib import Path
from logging.handlers import RotatingFileHandler
from conf import setting

log_path = setting.FILE_PATH['LOG']
if not os.path.exists(log_path):
    os.mkdir(log_path)

logfile_name = Path(log_path) / f'test_{time.strftime("%Y%m%d%H%M%S")}.log'

class Recordlog:
    def output_logging(self):
        logger = logging.getLogger(__name__)
        #防止log重复打印日志
        if not logger.handlers:
            logger.setLevel(setting.LOG_LEVEL)
            log_format = logging.Formatter(
                "%(asctime)s - %(filename)s:%(lineno)d - [%(module)s:%(funcName)s] - %(name)s - %(levelname)s - %(message)s"
            )
            fh = RotatingFileHandler(
                filename=logfile_name,
                maxBytes=1024 * 1024 * 10,
                mode='a',
                backupCount=3,
                encoding='utf-8'
            )
            fh.setFormatter(log_format)
            fh.setLevel(setting.LOG_LEVEL)
            logger.addHandler(fh)

            sh = logging.StreamHandler
            sh.setFormatter(log_format)
            sh.setLevel(setting.LOG_LEVEL)

            logger.addHandler(sh)
        return logger

logapi = Recordlog()
logs = logapi.output_logging()