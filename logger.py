import logging
from logging.handlers import TimedRotatingFileHandler
from rich.logging import RichHandler
import os
import re
import time


class Logger():
    logger: logging.Logger
    dynamic: bool
    CREATED_TIME: time.struct_time
    FN_FORMAT: str
    PATH: str
    STORE_FN: str
    LATEST_FN: str
    def filepath(self, filename) -> str: pass
    def update_time(self) -> time.struct_time: pass
    def refresh_fn(self) -> str: pass
    def get_log_head(self) -> str: pass
    def get_time_from_file(self, filepath) -> str: pass


class RotatingFileHandler(TimedRotatingFileHandler):
    upper_logger: Logger

    # Pre set filename which will be renamed to
    def rotation_filename(self, default_name: str) -> str:
        if self.upper_logger.dynamic:
            new_name = self.upper_logger.get_time_from_file(default_name)
            if new_name:
                new_name = new_name+".log"
                return super().rotation_filename(self.upper_logger.filepath(new_name))
            else:
                return super().rotation_filename(self.upper_logger.filepath(default_name))
        else:
            return super().rotation_filename(default_name)

    # Rename
    def rotate(self, source: str, dest: str) -> None:
        if self.upper_logger.dynamic:
            # rename: source -> dest
            super().rotate(source, dest)

        self.upper_logger.update_time()
        log_fp = self.upper_logger.filepath(
            self.upper_logger.LATEST_FN if self.upper_logger.dynamic else self.upper_logger.STORE_FN)
        self.baseFilename = log_fp
        open(log_fp, "w", encoding="utf-8").write(self.upper_logger.get_log_head())

    def doRollover(self) -> None:
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(self.suffix, timeTuple))
        if self.upper_logger.dynamic and os.path.exists(dfn):
            os.remove(dfn)
        self.rotate(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


class Logger():

    logger = logging.getLogger(__name__)
    dynamic = False
    CREATED_TIME = time.localtime()
    FN_FORMAT = '%Y%m%d%H%M%S.log'
    PATH = "./logs/"
    STORE_FN = f"{time.strftime(FN_FORMAT, CREATED_TIME)}"
    LATEST_FN = "latest.log"

    def __init__(self, fn_format=FN_FORMAT, path=PATH, latest_fn=LATEST_FN, dynamic=False) -> None:
        """A log helper

        Args:
            fn_format (str, optional): filename's format with time. Defaults to FN_FORMAT.
            path (str, optional): path of logged files. Defaults to PATH.
            latest_fn (str, optional): the filename of the current and the latest logged file (dynamic only). Defaults to LATEST_FN.
            dynamic (bool, optional): enable dynamic logging. Defaults to False.
        """
        self.dynamic = dynamic
        self.PATH = path
        self.FN_FORMAT = fn_format
        self.LATEST_FN = latest_fn
        self.STORE_FN = f"{time.strftime(fn_format, self.CREATED_TIME)}"
        log_fp = self.refresh_fn()
        HANDLER: dict[str, logging.Handler(RichHandler, RotatingFileHandler)] = {
            "SHELL": RichHandler(),
            "FILE": RotatingFileHandler(log_fp, interval=1, when="MIDNIGHT")
        }
        HANDLER["FILE"].upper_logger = self
        FORMAT: dict[str, str] = {
            "SHELL": '%(message)s',
            "FILE": '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'
        }
        self.logger.setLevel(logging.DEBUG)
        HANDLER["SHELL"].setLevel(logging.DEBUG)
        HANDLER["FILE"].setLevel(logging.DEBUG)
        HANDLER["SHELL"].setFormatter(logging.Formatter(FORMAT["SHELL"], datefmt="%H:%M:%S"))
        HANDLER["FILE"].setFormatter(logging.Formatter(FORMAT["FILE"], datefmt="%H:%M:%S"))
        HANDLER["FILE"].suffix = ""
        self.logger.addHandler(HANDLER["SHELL"])
        self.logger.addHandler(HANDLER["FILE"])
        open(log_fp, "w", encoding="utf-8").write(self.get_log_head())

    def filepath(self, filename):
        return self.PATH+filename

    def update_time(self):
        self.CREATED_TIME = time.localtime()
        self.STORE_FN = f"{time.strftime(self.FN_FORMAT, self.CREATED_TIME)}"
        return self.CREATED_TIME

    def refresh_fn(self):
        # rename latest.txt
        latest_fp = self.filepath(self.LATEST_FN)
        if not os.path.exists(self.PATH):
            os.makedirs(self.PATH)
        new_name = self.get_time_from_file(latest_fp)
        # make latest.log -> TIME_FORMATED.log when starting
        if new_name:
            new_name = new_name+".log"
            os.rename(
                self.filepath(self.LATEST_FN),
                self.filepath(new_name)
            )
        if self.dynamic:
            # latest.txt
            return self.filepath(self.LATEST_FN)
        else:
            # TIME_FORMATED.log
            return self.filepath(self.STORE_FN)

    def get_log_head(self):
        return f"# Logging from {time.strftime('%a %b %d %Y %H:%M:%S GMT+0800 (中国标准时间)', self.CREATED_TIME)}\n"

    def get_time_from_file(self, filepath):
        if os.path.exists(filepath):
            first_line = open(filepath, "r", encoding="utf-8").readline()
            try:
                time_str: str = re.findall(r"Logging from (.+?) GMT+", first_line)[0]
                loc_time = time.strptime(time_str, "%a %b %d %Y %H:%M:%S")
                time_str = time.strftime("%Y%m%d%H%M%S", loc_time)
                return time_str
            except:
                if filepath == self.filepath(self.LATEST_FN):
                    os.remove(filepath)
                return False
        else:
            return False


logger = Logger(path="./logs/", dynamic=True).logger
