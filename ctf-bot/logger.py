import colorama
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import LogRecord, StreamHandler
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


class DynamicTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    This modified class impliments features below:

    - Interaction with custom class `Logger`
    - When dynamic, rename `latest.log` to `<TIME_STRING>.log`
    - When not dynamic, create `<TIME_STRING>.log`
    - Remove `[format][/]` pattern when `RichHandler` is used and option `markup` is `True`
    """
    upper_logger: Logger

    def handle(self, record: LogRecord) -> bool:
        """Modify message, for RichHandler will contains color sysbols like `[red][/]`"""
        markup = record.__dict__.get("markup")
        if markup:
            splited_list = re.split(r"(\[.+?\])", record.msg)
            for i in range(len(splited_list)):
                if re.search(r"^\[.+?\]$", splited_list[i]):
                    if i > 0 and splited_list[i-1] == "\\":
                        splited_list[i-1] = ""
                    else:
                        splited_list[i] = ""
            record.msg = record.message = "".join(splited_list)
            record.msg
        return super().handle(record)

    def rotation_filename(self, default_name: str) -> str:
        """Pre-set and return filename which will soon be renamed to"""
        if self.upper_logger.dynamic:
            new_name = self.upper_logger.get_time_from_file(default_name)
            if new_name:
                new_name = new_name+".log"
                return super().rotation_filename(self.upper_logger.filepath(new_name))
            else:
                return super().rotation_filename(self.upper_logger.filepath(default_name))
        else:
            return super().rotation_filename(default_name)

    # Rename when on dynamic
    def rotate(self, source: str, dest: str) -> None:
        """Rename when dynamic, create new files, and write head (log time) to the new log file"""
        if self.upper_logger.dynamic:
            # Rename: source -> dest
            super().rotate(source, dest)

        self.upper_logger.update_time()
        log_fp = self.upper_logger.filepath(
            self.upper_logger.LATEST_FN if self.upper_logger.dynamic else self.upper_logger.STORE_FN)
        self.baseFilename = log_fp
        open(log_fp, "w", encoding="utf-8").write(self.upper_logger.get_log_head())

    def doRollover(self) -> None:
        """
        The original method would delete the log file whose name is equal to renamed old log
        file. But this process is only required when dynamic. So as to modify this method.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # Get the time that this sequence started at and make it a TimeTuple
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
        if self.upper_logger.dynamic and os.path.exists(dfn):  # Edited
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


class ColorStreamFormatter(logging.Formatter):
    """@deprecated

    A Formatter to impliment custom color format inherited from `logging.Formatter`.

    The class is created to support formatting the TIME, LEVEL, MESSAGE with colors for
    `StreamHandler`. Like how default formater is used, its usages are as following:

    ```python
    handler = StreamHandler()
    handler.setFormatter(
        '{1}%(asctime)s{0} {2}%(levelname)-8s{0} {3}%(message)s{0}')
    ```
    See also: `__init__`
    """
    RESET_COLOR = colorama.Style.RESET_ALL
    TIME_COLOR = colorama.Fore.CYAN
    LEVEL_COLOR = {
        logging.DEBUG: colorama.Fore.GREEN,
        logging.INFO: colorama.Fore.BLUE,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
        logging.CRITICAL: colorama.Fore.BLACK + colorama.Back.LIGHTRED_EX
    }
    MSG_COLOR = {
        logging.DEBUG: colorama.Style.RESET_ALL,
        logging.INFO: colorama.Style.RESET_ALL,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
        logging.CRITICAL: colorama.Fore.RED
    }

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, *,
                 defaults=None) -> None:
        """
        Modify the initialization to save args for modified method `format`.

        Args:
            fmt (str, optional): It has several format position:
            - {0} Reset format
            - {1} time style
            - {2} level style
            - {3} message style
        """
        self.pre_fmt = fmt
        self.__args = [datefmt, style, validate, defaults]
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    def format(self, record: LogRecord) -> str:
        """Add colors to record"""

        level_color = self.LEVEL_COLOR.get(record.levelno)
        msg_color = self.MSG_COLOR.get(record.levelno)

        # Format patterns like {0} in str
        new_fmt = self.pre_fmt.format(
            self.RESET_COLOR, self.TIME_COLOR, level_color, msg_color)

        self.__init__(
            new_fmt, self.__args[0], self.__args[1], self.__args[2], defaults=self.__args[3])
        return super().format(record)


class Logger():
    """
    A log helper

    It will prompt logging in both console and file. And make the file log rotated at
    midnight. This Helper also offers options `dynamic` which will log `latest.log` and
    rename it to time-based file name when new `latest.log` is supposed to be create or
    when the log file is roteted.
    """

    logger = logging.getLogger(__name__)
    dynamic = False
    CREATED_TIME = time.localtime()
    FN_FORMAT = '%Y%m%d%H%M%S.log'
    PATH = "./logs/"
    STORE_FN = f"{time.strftime(FN_FORMAT, CREATED_TIME)}"
    LATEST_FN = "latest.log"

    def __init__(self, fn_format=FN_FORMAT, path=PATH, latest_fn=LATEST_FN, dynamic=False) -> None:
        """
        Initialize the Logger. Store some settings and create log handlers on shell and
        on file. Log handler is default to `RichHandler` for shell which support easy
        colorifying, and to modified `TimedRotatingFileHandler` for file. The modified
        file handler is `DynamicTimedRotatingFileHandler`, created for mostly supporting
        dynamic file logging and removing color symbols like `[red][/]` because of
        functions from `RichHandler`.

        Args:
            fn_format (str, optional): filename's format with time.
            path (str, optional): path of logged files.
            latest_fn (str, optional): the filename of the current and the latest logged file (dynamic only).
            dynamic (bool, optional): enable dynamic logging.
        """
        self.dynamic = dynamic
        self.PATH = path
        self.FN_FORMAT = fn_format
        self.LATEST_FN = latest_fn
        self.STORE_FN = f"{time.strftime(fn_format, self.CREATED_TIME)}"
        log_fp = self.refresh_fn()
        HANDLER: dict[str, logging.Handler(RichHandler, DynamicTimedRotatingFileHandler)] = {
            "SHELL": RichHandler(),
            "FILE": DynamicTimedRotatingFileHandler(log_fp, interval=1, when="MIDNIGHT")
        }
        # Deliver the logger so that the handler could visit properties and methods here
        HANDLER["FILE"].upper_logger = self
        FORMAT: dict[str, str] = {
            "SHELL": '%(message)s',
            "FILE": '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'
        }
        self.logger.setLevel(logging.DEBUG)
        HANDLER["SHELL"].setLevel(logging.DEBUG)
        HANDLER["FILE"].setLevel(logging.DEBUG)
        HANDLER["SHELL"].setFormatter(logging.Formatter(
            FORMAT["SHELL"], datefmt="%H:%M:%S"))
        HANDLER["FILE"].setFormatter(logging.Formatter(
            FORMAT["FILE"], datefmt="%H:%M:%S"))
        HANDLER["FILE"].suffix = ""
        self.logger.addHandler(HANDLER["SHELL"])
        self.logger.addHandler(HANDLER["FILE"])
        open(log_fp, "w", encoding="utf-8").write(self.get_log_head())

    def filepath(self, filename):
        """Generate relative filepath according to the given file"""
        return self.PATH+filename

    def update_time(self):
        """Update everything related to logging time"""
        self.CREATED_TIME = time.localtime()
        self.STORE_FN = f"{time.strftime(self.FN_FORMAT, self.CREATED_TIME)}"
        return self.CREATED_TIME

    def refresh_fn(self):
        """Get the log name according to `dynamic`. Also rename `latest.log` to time-based name"""
        # Rename latest.txt
        latest_fp = self.filepath(self.LATEST_FN)
        if not os.path.exists(self.PATH):
            os.makedirs(self.PATH)
        new_name = self.get_time_from_file(latest_fp)
        # Make latest.log -> TIME_FORMATED.log when starting
        if new_name:
            new_name = new_name+".log"
            # Rename the existed `latest.log`
            os.rename(
                self.filepath(self.LATEST_FN),
                self.filepath(new_name)
            )
        if self.dynamic:
            # Latest.txt
            return self.filepath(self.LATEST_FN)
        else:
            # TIME_FORMATED.log
            return self.filepath(self.STORE_FN)

    def get_log_head(self):
        """Generate a string which will be put at the head of a log file"""
        return f"# Logging from {time.strftime('%a %b %d %Y %H:%M:%S GMT+0800 (中国标准时间)', self.CREATED_TIME)}\n"

    def get_time_from_file(self, filepath):
        """Get a time string (looks like the time-based log file name) by reading the head of a specific log name"""
        if os.path.exists(filepath):
            first_line = open(filepath, "r", encoding="utf-8").readline()
            try:
                time_str: str = re.findall(
                    r"Logging from (.+?) GMT+", first_line)[0]
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
"""
A custom logger

Use `logger.log` to log in default levl. \\
Use `logger.<level>` to log in a specific level. \\
Use `extra` param in `logger.log("text", extra=...)` to do some extra settings.

Levels: `debug`, `info`, `warning`, `error`, `critical`

To look up colors, See https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
"""


class Extra:
    """
    Predefined value of param `extra` in `logger.log`
    """

    MARK_UP = {"markup": True}
    """
    Enable colorifying once for logging

    Using in following ways enables to output string in red
    ```python
    import Extra.MARK_UP
    logger.log("[red]text[/]", extra=MARK_UP)
    ```
    - Note: Use `\[` in string to escape `[]` pattern.
    """

    NO_HLT = {"highlighter": None}
    """
    Disable automatically highlighting once for logging

    Example as below
    ```python
    import Extra.NO_HLT
    logger.log("[red]text[/]", extra=NO_HLT)
    ```
    """

    PURE_MARK = {"markup": True, "highlighter": None}
    """
    A combination between `MARK_UP` and `NO_HLT`

    Using in following way will enable colorifying and disable automatically
    highlightingonce once for logging
    ```python
    import Extra.PURE_MARK
    logger.log("[red]text[/]", extra=PURE_MARK)
    ```
    """
