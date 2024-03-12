from Entity.Library import Library

library = Library("Data/release-book-bot-53308775461c.json", "릴리즈 도서 목록 - 연동 실험", "Data/2024-1_ActiveUser.csv")

library.rent_book(20231592, "이펙티브 자바")
print(library.check_book("이펙티브 자바"))
print(library.check_user(20231592))
library.return_book(20231592, "이펙티브 자바")
