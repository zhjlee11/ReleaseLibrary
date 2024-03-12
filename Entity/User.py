class User:
    def __init__(self,
                 student_no: int,
                 name: str,
                 phone_number: int):
        self.student_no = student_no
        self.name = name
        self.phone_number = phone_number

        self.rented_books = []

    def __str__(self) -> str:
        return f"학번:{self.student_no} | 이름:{self.name} | 전화번호:{self.phone_number}"

    def reset(self) -> None:
        self.rented_books = []