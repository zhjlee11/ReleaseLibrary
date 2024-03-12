class NotRentedException(Exception):
    def __init__(self):
        super().__init__(f"대여되지 않은 책입니다.")

class DifferentRentedOneException(Exception):
    def __init__(self):
        super().__init__(f"다른 사람이 대여한 책입니다.")