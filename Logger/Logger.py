import datetime
import os
from copy import deepcopy
from Config import Config
from typing import *


class Logger:
    def __init__(self,
                 log_path: str,
                 timezone: datetime.timezone = datetime.timezone(datetime.timedelta(hours=9))):
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        self.log_path = log_path
        self.timezone = timezone

    def _getNowDate(self):
        return datetime.datetime.now(tz=self.timezone).date()

    def _getLogFilePath(self):
        return os.path.join(self.log_path, f"Log_{self._getNowDate()}.log")

    def log(self,
            type: str,
            result: str,
            error_message: str,
            **kwargs):

        line = deepcopy(Config.LOG_FORMAT)
        line = line.replace("<DATE>", self._getNowDate().strftime(Config.DATE_FORMAT))
        line = line.replace("<TYPE>", type)
        line = line.replace("<RESULT>", result)

        detail = ""
        if result == "success":
            if type == Config.RENT_BOOK:
                detail = f"{kwargs['student_no']} -> 「{kwargs['book_name']}」 대출"
            elif type == Config.RETURN_BOOK:
                detail = f"{kwargs['student_no']} -> 「{kwargs['book_name']}」 반납"
            elif type == Config.CHECK_USER:
                detail = f"유저 {kwargs['student_no']} 정보 조회"
            elif type == Config.CHECK_BOOK:
                detail = f"책 「{kwargs['book_name']}」 정보 조회"
            elif type == Config.CHECK_USER:
                detail = f"반납 기한 {kwargs['period_days']} 이내 대여자 조회"
            elif type == Config.CHECK_USER:
                detail = f"연체자 조회"
        else:
            detail = error_message

        line = line.replace("<DETAIL>", detail)

        with open(self._getLogFilePath(), "a") as f:
            f.write(f"{line}\n")
