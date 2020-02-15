import logging
from datetime import datetime

def log_time(func):
    def wrapper(*args, **kw):
        time_start = datetime.now()
        ret = func(*args, **kw)
        time_end = datetime.now()
        logging.info("start:{}, end:{}, total time usage:{}".format(time_start,time_end,time_end - time_start))
        return ret
    return wrapper