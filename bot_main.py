import discord
import requests

ADMIN_LIST = [
    313923862276341761,
]

API_ADDRESS = "http://127.0.0.1:8080"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/도서'):
        if message.content.startswith('/도서 ping'):
            await message.reply(f'### pong\n[user id : {message.author.id}]')
        elif message.content.startswith('/도서 대여 '):
            inp = message.content.replace('/도서 대여 ', '').split(" ")
            book_name = ' '.join(inp[1:])
            try:
                student_no = int(inp[0])
            except ValueError as e:
                await message.reply('대여에 실패하였습니다.\n옳지 않은 학번입니다.')
                return

            result = requests.post(f"{API_ADDRESS}/rent", json={"student_no":student_no, "book_name":book_name}).json()
            if result["result"]=="success":
                await message.reply('성공적으로 대여하였습니다.')
            else:
                await message.reply(f'대여에 실패하였습니다.\n{result["errorMessage"]}')

        elif message.content.startswith('/도서 반납 '):
            inp = message.content.replace('/도서 반납 ', '').split(" ")
            book_name = ' '.join(inp[1:])
            try:
                student_no = int(inp[0])
            except ValueError as e:
                await message.reply('반납에 실패하였습니다.\n옳지 않은 학번입니다.')
                return

            result = requests.post(f"{API_ADDRESS}/return", json={"student_no": student_no, "book_name": book_name}).json()
            if result["result"] == "success":
                await message.reply('성공적으로 반납하였습니다.')
            else:
                await message.reply(f'반납에 실패하였습니다.\n{result["errorMessage"]}')

        elif message.content.startswith('/도서 조회 사용자 '):
            student_no = message.content.replace('/도서 조회 사용자 ', '')
            try:
                student_no = int(student_no)
            except ValueError as e:
                await message.reply('사용자 조회에 실패하였습니다.\n옳지 않은 학번입니다.')
                return

            result = requests.post(f"{API_ADDRESS}/check_user", json={"student_no": student_no}).json()
            if result["result"] == "success":
                content = f"# {result['data']['name']}님의 사용자 정보\n"
                content += f"*학번 : {result['data']['student_no']}*\n"
                content += "\n"
                for book_name, rent_info in result['data']['rented_books'].items():
                    content += f"## {book_name}\n"
                    content += f"대출 날짜 : {rent_info['rented_date']}\n"
                    content += f"반납 기한 : {rent_info['return_deadline']}\n"
                await message.reply(content)
            else:
                await message.reply(f'사용자 조회에 실패하였습니다.\n{result["errorMessage"]}')

        elif message.content.startswith('/도서 조회 책 '):
            book_name = message.content.replace('/도서 조회 책 ', '')

            result = requests.post(f"{API_ADDRESS}/check_book", json={"book_name": book_name}).json()
            if result["result"] == "success":
                content = f"# {result['data']['book_name']} 정보\n"
                content += f"대여 가능 여부 : {'가능' if result['data']['can_rent'] else '불가능'}\n"
                content += f"상태 : {'대출 중' if result['data']['is_rented'] else '비치 중'}\n"
                if result['data']['can_rent'] and result['data']['is_rented']:
                    content += f"예상 반납 날짜 : {result['data']['return_deadline']}"

                await message.reply(content)
            else:
                await message.reply(f'도서 조회에 실패하였습니다.\n{result["errorMessage"]}')
        elif message.content.startswith('/도서 조회 반납예정 '):
            if message.author.id in ADMIN_LIST:
                period_days = message.content.replace('/도서 조회 반납예정 ', '')
                try:
                    period_days = int(period_days)
                except ValueError as e:
                    await message.reply('반납예정 조회에 실패하였습니다.\n옳지 않은 날짜입니다.')
                    return

                result = requests.post(f"{API_ADDRESS}/get_imminent_user", json={"period_days": period_days}).json()
                if result["result"] == "success":
                    content = f"# 반납 예정자 정보\n"
                    for student_no, info_list in result['data'].items():
                        if len(info_list) != 0:
                            for info in info_list:
                                content += f"- {info['name']}({student_no}) : {info['book']} [{info['overdue_days']}일 후 반납]\n"

                    await message.reply(content)
                else:
                    await message.reply(f'반납예정자 조회에 실패하였습니다.\n{result["errorMessage"]}')
            else:
                await message.reply(f'권한이 없습니다.')

        elif message.content.startswith('/도서 조회 연체'):
            if message.author.id in ADMIN_LIST:
                result = requests.get(f"{API_ADDRESS}/get_overdue_user").json()
                if result["result"] == "success":
                    content = f"# 연체자 정보\n"
                    for student_no, info_list in result['data'].items():
                        if len(info_list)!=0:
                            for info in info_list:
                                content += f"- {info['name']}({student_no}) : {info['book']} [{info['overdue_days']}일 연체]\n"

                    await message.reply(content)
                else:
                    await message.reply(f'연체자 조회에 실패하였습니다.\n{result["errorMessage"]}')
            else:
                await message.reply(f'권한이 없습니다.')

        elif message.content.startswith('/도서 목록'):
            result = requests.get(f"{API_ADDRESS}/get_book_list").json()
            if result["result"] == "success":
                content = f"# Release 도서 목록\n"
                content += f"*취소선이 그어진 책은 현재 대여가 불가능한 책입니다.*\n\n"
                for book in result["data"]:
                    book_name = book["book_name"]
                    if not book["available"]:
                        book_name = f"~~{book_name}~~"
                    content += f"> {book_name}\n"
                await message.reply(content)
            else:
                await message.reply(f'도서 목록 조회에 실패하였습니다.\n{result["errorMessage"]}')
        else:
            content = f"# Release 도서 관리 챗봇 명령어 도움말\n"
            content += f"## /도서 목록\n"
            content += f"대여 가능한 도서 목록을 확인합니다.\n"
            content += f"## /도서 대여 [학번] [도서 이름]\n"
            content += f"도서를 대여합니다.\n"
            content += f"## /도서 반납 [학번] [도서 이름]\n"
            content += f"도서를 반납합니다.\n"
            content += f"## /도서 조회 사용자 [학번]\n"
            content += f"사용자의 정보를 확인합니다.\n"
            content += f"## /도서 조회 책 [도서 이름]\n"
            content += f"도서의 정보를 확인합니다.\n"
            if message.author.id in ADMIN_LIST:
                content += f"## /도서 조회 반납예정 [여유 반납 날짜]\n"
                content += f"여유 반납 날짜 이내로 반납을 해야하는 책이 있는 유저를 출력합니다.\n"
                content += f"## /도서 조회 연체\n"
                content += f"연체자를 확인합니다.\n"

            await message.reply(content)

if __name__=="__main__":
    with open("token", "r") as f:
        client.run(f.read())