import datetime
import gspread
import pandas as pd
from Entity.User import User
from Entity.Book import Book
from Exception.RentException import *
from Exception.ReturnException import *
from Config import Config


class Library:
    def __init__(self,
                 token_path: str,
                 spreadsheet_name: str,
                 active_users_path: str,
                 worksheet: str = "시트1",
                 timezome: datetime.timezone = datetime.timezone(datetime.timedelta(hours=9))):
        self.timezone = timezome

        gc = gspread.service_account(token_path)
        sh = gc.open(spreadsheet_name)
        self.book_sheet = sh.worksheet(worksheet)
        self.book_info = {}

        active_users_dict = pd.read_csv(active_users_path).to_dict(orient="records")
        self.active_users = {int(row["학번"]): User(int(row["학번"]), row["이름"], row["전화번호"]) for row in active_users_dict}

        self.refresh()

    def getNowDate(self):
        return datetime.datetime.now(tz=self.timezone).date()

    def refreshBookInfo(self):
        book_info = self.book_sheet.get_all_records()
        self.book_info = {}
        for ind, row in enumerate(book_info):
            book = Book(ind + 2,
                        row["제목"],
                        not row["대여 가능 여부"] == "X",
                        row["현재 대여 여부"] == "O",
                        datetime.datetime.strptime(row["대여 날짜"], Config.DATE_FORMAT).date() if len(
                            row["대여 날짜"]) != 0 else None,
                        datetime.datetime.strptime(row["반납 예정 날짜"], Config.DATE_FORMAT).date() if len(
                            row["반납 예정 날짜"]) != 0 else None,
                        row["대여자 학번"] if type(row["대여자 학번"]) == int else None)
            self.book_info[book.id] = book
        self.book_name_query = {book.name: book.id for book in self.book_info.values()}

    def refreshUserInfo(self):
        for _, user in self.active_users.items():
            user.reset()
        for _, book in self.book_info.items():
            if book.rented_student_no is not None:
                if book.rented_student_no in self.active_users.keys():
                    self.active_users[book.rented_student_no].rented_books.append(book.id)
                else:
                    raise InvalidUserException

    def refresh(self):
        self.refreshBookInfo()
        self.refreshUserInfo()

    def rent_book(self,
                  student_no: int,
                  book_name: str):
        self.refresh()

        if student_no not in self.active_users.keys():
            raise InvalidUserException
        if book_name not in self.book_name_query.keys():
            raise InvalidBookException

        user = self.active_users[student_no]
        book = self.book_info[self.book_name_query[book_name]]

        if not book.can_rent:
            raise CanNotRentBookException
        if len(user.rented_books) >= Config.BOOK_NUM_PER_ONE:
            raise MaxBookException
        if book.is_rented:
            raise AlreadyRentedException

        now_date = self.getNowDate()
        self.book_sheet.update(f"C{book.id}:G{book.id}",
                               [["O",
                                 now_date.strftime(Config.DATE_FORMAT),
                                 (now_date + datetime.timedelta(days=Config.DAYS_OF_RENTAL)).strftime(
                                     Config.DATE_FORMAT),
                                 user.student_no,
                                 user.name]])

    def return_book(self,
                    student_no: int,
                    book_name: str):
        self.refresh()

        if student_no not in self.active_users.keys():
            raise InvalidUserException
        if book_name not in self.book_name_query.keys():
            raise InvalidBookException

        book = self.book_info[self.book_name_query[book_name]]

        if not book.is_rented:
            raise NotRentedException
        if book.rented_student_no != student_no:
            raise DifferentRentedOneException

        self.book_sheet.update(f"C{book.id}:G{book.id}", [[""] * 5])

    def check_book(self,
                   book_name: str):
        self.refresh()
        if book_name not in self.book_name_query.keys():
            raise InvalidBookException

        book = self.book_info[self.book_name_query[book_name]]

        result = {"book_name": book.name,
                  "can_rent": book.can_rent,
                  "is_rented": book.is_rented,
                  "return_deadline": datetime.date.strftime(book.return_deadline, Config.DATE_FORMAT) if book.return_deadline is not None else None}

        return result

    def check_user(self,
                   student_no: int):
        self.refresh()
        if student_no not in self.active_users.keys():
            raise InvalidUserException

        user = self.active_users[student_no]

        result = {"student_no" : user.student_no, "name":user.name, "rented_books":{}}

        for book_id in user.rented_books:
            book = self.book_info[book_id]
            result["rented_books"][book.name] = {
                "rented_date" :  datetime.date.strftime(book.rent_date, Config.DATE_FORMAT),
                "return_deadline" :  datetime.date.strftime(book.return_deadline, Config.DATE_FORMAT)
            }

        return result

    def get_imminent_user(self,
                          period_days: int):
        self.refresh()
        result = {}

        now = self.getNowDate()
        for user in self.active_users.values():
            result[user.student_no] = []

        for user in self.active_users.values():
            for book_id in user.rented_books:
                book = self.book_info[book_id]

                diff = (book.return_deadline - now).days
                if diff <= period_days and now <= book.return_deadline:
                    result[user.student_no].append({"name": user.name,
                                               "book": book.name,
                                               "overdue_days": diff})

        return result

    def get_overdue_user(self):
        self.refresh()
        result = {}

        now = self.getNowDate()
        for user in self.active_users.values():
            result[user.student_no] = []

        for user in self.active_users.values():
            for book_id in user.rented_books:
                book = self.book_info[book_id]
                if book.return_deadline < now:
                    result[user.student_no].append({"name": user.name,
                                               "book": book.name,
                                               "overdue_days": (now - book.return_deadline).days})


        return result
