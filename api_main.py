from flask import Flask, request, jsonify, Response
from flask_restx import Api, Resource
from Entity.Library import Library
from Exception.RentException import *
from Exception.ReturnException import *
from Logger.Logger import Logger
from Config import Config

app = Flask(__name__)
api = Api(app)

headers = {
    "Content-Type": "application/json"
}

@app.route('/rent', methods=['POST'])
def rent_book():
    json_data = request.get_json(force=True)
    student_no = int(json_data["student_no"])
    book_name = json_data["book_name"]

    result = {"result": "success", "errorMessage": ""}

    try:
        library.rent_book(student_no, book_name)
    except InvalidUserException as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)
    except InvalidBookException as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)
    except MaxBookException as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)
    except AlreadyRentedException as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)
    except CanNotRentBookException as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)

    logger.log(Config.RENT_BOOK, result["result"], result["errorMessage"], student_no=student_no, book_name=book_name)

    return jsonify(result)

@app.route('/return', methods=['POST'])
def return_book():
    json_data = request.get_json(force=True)
    student_no = int(json_data["student_no"])
    book_name = json_data["book_name"]

    result = {"result": "success", "errorMessage": ""}

    try:
        library.return_book(student_no, book_name)
    except InvalidUserException as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)
    except InvalidBookException as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)
    except NotRentedException as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)
    except DifferentRentedOneException as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)

    logger.log(Config.RETURN_BOOK, result["result"], result["errorMessage"], student_no=student_no, book_name=book_name)

    return jsonify(result)

@app.route('/check_book', methods=['POST'])
def check_book():
    json_data = request.get_json(force=True)
    book_name = json_data["book_name"]

    result = {"result": "success", "errorMessage": "", "data": None}

    try:
        data = library.check_book(book_name)
        result["data"] = data
    except InvalidBookException as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)

    logger.log(Config.CHECK_BOOK, result["result"], result["errorMessage"], book_name=book_name)

    return jsonify(result)

@app.route('/check_user', methods=['POST'])
def check_user():
    json_data = request.get_json(force=True)
    student_no = int(json_data["student_no"])

    result = {"result": "success", "errorMessage": "", "data": None}

    try:
        data = library.check_user(student_no)
        result["data"] = data
    except InvalidUserException as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)

    logger.log(Config.CHECK_USER, result["result"], result["errorMessage"], student_no=student_no)

    return jsonify(result)

@app.route('/get_imminent_user', methods=['POST'])
def get_imminent_user():
    json_data = request.get_json(force=True)
    period_days = int(json_data["period_days"])

    result = {"result": "success", "errorMessage": "", "data": None}

    try:
        data = library.get_imminent_user(period_days)
        result["data"] = data
    except Exception as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)

    logger.log(Config.CHECK_IMMINENT_USER, result["result"], result["errorMessage"], period_days=period_days)

    return jsonify(result)

@app.route('/get_overdue_user', methods=['GET'])
def get_overdue_user():
    result = {"result": "success", "errorMessage": "", "data": None}

    try:
        data = library.get_overdue_user()
        result["data"] = data
    except Exception as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)

    logger.log(Config.CHECK_OVERDUE_USER, result["result"], result["errorMessage"])

    return jsonify(result)

@app.route('/get_book_list', methods=['GET'])
def get_book_list():
    result = {"result": "success", "errorMessage": "", "data": None}

    try:
        data = library.get_book_list()
        result["data"] = data
    except Exception as e:
        result["result"] = "fail"
        result["errorMessage"] = str(e)

    logger.log(Config.GET_BOOK_LIST, result["result"], result["errorMessage"])

    return jsonify(result)


if __name__ == "__main__":
    library = Library("Data/release-book-bot-53308775461c.json", "릴리즈 도서 목록 - 연동 실험", "Data/2024-1_ActiveUser.csv")
    logger = Logger(log_path="./Log")
    app.run(debug=True, host='127.0.0.1', port=8080)
