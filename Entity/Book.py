import datetime

class Book:
    def __init__(self,
                 id: int,
                 name: str,
                 is_rented: bool,
                 rent_date: datetime.date,
                 rented_student_no: int):
        self.id = id
        self.name = name
        self.is_rented = is_rented
        self.rent_date = rent_date
        self.rented_student_no = rented_student_no
        
    def __str__(self):
        content = f"〈 {self.name} 〉\n"
        content += f"대여 가능 여부 : {'가능' if not self.is_rented else '불가능'}"
        return content