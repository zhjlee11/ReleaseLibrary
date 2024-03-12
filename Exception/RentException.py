class InvalidUserException(Exception):
    def __init__(self):
        super().__init__(f"옳지 않은 학번입니다.")

class InvalidBookException(Exception):
    def __init__(self):
        super().__init__(f"그러한 이름의 책은 존재하지 않습니다.")

class MaxBookException(Exception):
    def __init__(self):
        super().__init__(f"이미 최대한의 책 수량을 대여하셨습니다.")

class AlreadyRentedException(Exception):
    def __init__(self):
        super().__init__(f"이미 누군가가 대여한 책입니다.")