# Flask API 만들기
# GET API, POST API, XXX API
# @app.route("/path", methods=["GET"])
# 다음 주어진 함수를 API에 연결한다

# [API를 받을 때]
# GET, DELETE -> "쿼리" request.args.get("이름")
# POST, PUT -> "바디" request.get_json() -> 바디에 담겨 있는 걸 dictionary로!

# [API를 응답할 때]
# jsonify

# Flask DB 접근하기 정리
# 1) sql을 만든다
# 2) cursor.execute(sql)을 한다
# 3) 조회가 아닌 저장/수정/삭제라면 db.commit()을 한다

# JdbcTemplate을 그냥 사용하면, SQL 문자열을 그대로 쓰는거죠~
# DB의 종류를 바꾼다거나.. 아니면 우리가 좀 불편하다거나 (SQL을 직접 써야하니까)
# python에서도 JPA에 같은 ORM이 있습니다.
# 클래스(객체) = 테이블 --> 매핑


import pymysql
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
db = pymysql.connect(host='localhost', port=3306, user='root', password='1234', db='library', charset='utf8')
cursor = db.cursor()

@app.route("/page", methods=["GET"])
def home_page():
    return render_template('flask.html')

# http://127.0.0.1:5000/hello
# GET /hello -> Hello World
# GET에서 데이터를 받는 법 : Query /hello?num1=10&num2=20
@app.route("/hello", methods=["GET"])
def hello():
    sql = "select * from user"
    cursor.execute(sql)
    results = cursor.fetchall()
    # print(results)
    # return ""
    result_dict = []
    for result in results: # ((id, ..), (), (), ()) <- 안에 있는 () = result
        result_dict.append({
            "id": result[0],
            "name": result[1],
            "age": result[2]
        })
    return jsonify(result_dict)

# POST는 데이터를 어떻게?!
@app.route("/hello", methods=["POST"])
def post_hello():
    data = request.get_json()
    name = data["name"]
    age = data["age"]
    #sql = """INSERT INTO user (name, age) VALUES('%S', %S)""" % (name, age)
    sql = f"INSERT INTO user (name, age) VALUES('{name}', {age})"
    cursor.execute(sql)
    db.commit()
    return "OK"

    # a = int(request.args.get("num1"))
    # b = int(request.args.get("num2"))
    # return jsonify({
    #     "result": a+b
    # })

    # { "result": 결과 }

    # result = {
    #     "id": 3,
    #     "name": "Kitty",
    #     "age": 5
    # }
    # return jsonify(result)
# 출력되는 순서가 랜덤인 것 같음!
# {"id": 3, "name": "Kitty", "age": 5}

# PUT API를 한 번 만들어보자!
# 주어진 유저의 id를 받아서 주어진 이름과 주어진 나이로 변경하는 기능
# PUT은 데이터를 Body로!
@app.route("/user", methods=["PUT"])
def update_user():
    data = request.get_json()
    user_id = data["id"]
    name = data["name"]
    age = data["age"]
    sql = f"UPDATE user SET name = '{name}', age = {age} WHERE id = {user_id}"
    cursor.execute(sql)
    db.commit()
    return "OK"

# 우리 API는 주어진 id를 받아서 해당 id를 가진 유저를 제거하는 기능!
# path : /user, method = DELETE
# Query : id --> 유저 id
@app.route("/user", methods=["DELETE"])
def delete_user():
    user_id = request.args.get("id")
    sql = f"DELETE FROM user WHERE id = {user_id}"
    cursor.execute(sql)
    db.commit()
    return "OK"

if __name__ == '__main__':
    app.run(debug=True)
