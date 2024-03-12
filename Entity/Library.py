import datetime
import gspread
import pandas as pd
from Entity.User import User
from Entity.Book import Book
from Exception.RentException import *
from Config import Config


class Library:
    def __init__(self,
                 token_path: str,
                 spreadsheet_name: str,
                 active_users_path: str,
                 worksheet: str = "시트1"):
        gc = gspread.service_account(token_path)
        sh = gc.open(spreadsheet_name)
        self.book_sheet = sh.worksheet(worksheet)
        self.book_info = {}

        active_users_dict = pd.read_csv(active_users_path).to_dict(orient="records")
        self.active_users = {int(row["학번"]): User(int(row["학번"]), row["이름"], row["전화번호"]) for row in active_users_dict}

        self.refresh()

    def refreshBookInfo(self):
        book_info = self.book_sheet.get_all_records()
        self.book_info = {}
        for ind, row in enumerate(book_info):
            book = Book(ind + 2, row["제목"], row["대여 여부"] == "O", datetime.datetime.strptime(row["대여 날짜"], Config.DATE_FORMAT).date() if len(row["대여 날짜"])!=0 else None,
                        row["대여자 학번"] if type(row["대여자 학번"])==int else None)
            self.book_info[book.id] = book
        self.book_name_query = {book.name:book.id for book in self.book_info.values()}

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

        if len(user.rented_books) >= Config.BOOK_NUM_PER_ONE:
            raise MaxBookException
        if book.is_rented:
            raise AlreadyRentedException

        self.book_sheet.update(f"B{book.id}:E{book.id}",
                               [["O",
                                datetime.datetime.now().date().strftime(Config.DATE_FORMAT),
                                user.student_no,
                                user.name]])

    def return_book(self,
                    student_no: int,
                    book_name: str):
        self.refresh()
        pass