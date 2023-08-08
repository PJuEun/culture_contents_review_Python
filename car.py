# 자동차 판매 관리 시스템
# 현재 판매하려고 등록된 자동차들이 목록이 나와야 합니다.
# 차종, 차량 번호(119서울 2123), 가격, 등록된 일자, 예약중/판매중
# 자동차를 등록할 수 있어야 한다!
# 판매중인 자동차를 예약할 수 있어야 합니다!

# 추가할 세가지 기능이 있다!
# 1) 부장님이.. 우리 차량 중 몇 대 판매 / 몇 대 예약 궁금하다!
# --> 현재 판매중 10대, 예약 중 5대
# 2) 현재 우리가 판매하고(판매, 예약) 있는 자동차 가격의 총합이 궁금하다!
#       자동차 가격의 총합을 구해야 하는데 -> 어디서 총합을 구할거냐?!
#       예를 들어서.. [1] 지금 JS에서 덧셈을 할수도 있음
#                   [2] python에서 할수도 있음
#                   [3] DB에서 덧셈도 하고 평균도 구할 수 있음
# 3) 현재 우리가 판매하고(판매, 예약) 있는 자동차 가격의 평균이 궁금하다!

# 현실세계도 마찬가지인데 "동시에"라는 개념이 있습니다.
# 제가 전화를 거는데, 하필 그사람도 저한테 전화를 걸면 어떻게 되죠?
# 둘 다 통화중이 나오죠
# 동시성 : 동시에 처리되는 성질

# 성능 -> 우리가 사용하는 pymysql은 "동시에" SQL을 못써요!
# (Java는 가능!)

# 우리가 작성한 JS코드는 동시에 API 2개를 호출!
# select * from car; / select sum(price), avg(price) from car;
# 해결방법
# 1) 꼼수 : JS에서 GET /car가 완전히 끝난 다음에 GET /car/stat을 호출
# -> /car안의 success에 /car/stat을 넣어줌

# 2) 정석
# 프로세스 / 스레드
# 프로세스 : 작업관리자(ps aux) = 지금 돌고 있는 프로그램
# 스레드
# 두개의 농장이 있음, 농장 1개 = 프로세스 1개
# A 농장 : 일꾼 1명 - 사과도 따고, 벼 농사도 짓고,,
# B 농장 : 일꾼 3명 - 사과를 전용 1명 + 벼 농사 2명
# 스레드는 일꾼!!

# 자 그러면 "동시성"에 대한 이해를 조금 더 할건데
# A랑 B랑 동시에 어떤 페이지를 확인함

# single-thread
# 그런데 하필 그 프로그램에 일꾼이 1명이야!
# 단 0.00000001초라도 늦게 들어온 사람에게 기다려~ 라고 말하고~ 먼저 온 사람 처리
# 나중에 온 사람 다 끝나고 처리

# multi-thread
# 그런데 일꾼이 여러명이야!
# 누가 0.00000001초라도 먼저 왔는지는 중요하지 않고 아무튼 일꾼이 각각 배정되서
# A랑 B의 기능 모두를 처리

# 정석 해결책
# 1. SQL을 동시에 한 명만 처리할 수 있게 한다 -> 어렵다
# 2. 우리 flask는 일꾼을 한 명만 둔다
# 참고로 Java Spring은 당연히 multi-thread이고
# pymysql을 안쓰고 jdbcTemplate을 사용하는데

# GET / POST / PUT
# path : /car
# id, name(차종), number(차량번호), price(가격), date(등록된일자), state(예약중0/판매중1)

import pymysql
from flask import Flask, jsonify, request, render_template
from datetime import datetime
from enum import Enum

app = Flask(__name__)
db = pymysql.connect(host='localhost', port=3306, user='root', password='1234', db='car', charset='utf8')
cursor = db.cursor()

@app.route("/car_save", methods=["GET"])
def car_save_page():
    return render_template('car_save.html')

@app.route("/car_list", methods=["GET"])
def car_list_page():
    return render_template('car_list.html')

# 만들어야 할 3가지 기능
# 저장 기능 -> 조회 기능 -> 수정 기능

class CarState(Enum):
    ON_SALE = ""
    ON_RESERVATION = ""

# POST
@app.route("/car", methods=["POST"])
def save_car():
    data = request.get_json()
    name = data["name"]
    number = data["number"]
    price = data["price"]

    # date = data["date"]
    # 날짜 시간 --> 날짜 date / 시간 time / 날짜+시간 datetime
    # datetime.todqy() -> "오늘"을 가져올 수 있어!
    # 결국 오늘이라는 날짜를 가져오는 이유는 DB에 날짜를 넣어주기 위함!
    date = get_today()

    #state = data["state"]
    # 일반적으로 "상태"관리는 숫자보다는 문자열이 좋고
    # 단순 문자열보다는 Enum 이란 것으로 관리하는게 좋다~
    # "상태"는 그냥 문자열과 조금 다른 특징이 있다
    # 그냥 문자열 (ex. 이름) abc, lannstark, stark, ...
    # "상태" ON_SALE / ON_RESERVATION
    # 모아서 관리할 수 있게 상수로 편하게 만드는데~ 그 방식이 바로 Enum
    state = CarState.ON_SALE.name

    sql = f"INSERT INTO car (name, number, price, date, state) VALUES('{name}', '{number}', {price}, '{date}', '{state}')"
    cursor.execute(sql)
    db.commit()
    return "OK"

# "오늘"이란 개념에 사실 함정이 있다
# 한국 기준 오늘이랑 미국 기준 오늘이랑.. 다 다름
# "시차" (타임존)
# 문제는 "배포"를 하면... 우리 컴퓨터에서 실행되는게 아니다!
# 배포를 하면 우리가 빌린 컴퓨터에서 실행됨! <-- 빌린 컴퓨터의 타임존 설정!
def get_today():
    today = datetime.today() # 컴퓨터의 타임존을 따라감!
    return today.strftime("%Y-%m-%d")


# GET
@app.route("/car", methods=["GET"])
def get_car():
    sql = "select * from car"
    cursor.execute(sql)
    results = cursor.fetchall()
    result_dict = []

    for result in results:
        result_dict.append({
            "id": result[0],
            "name": result[1],
            "number": result[2],
            "price" : result[3],
            "date" : result[4].strftime("%Y-%m-%d"),
            "state" : result[5]
        })
    return jsonify(result_dict)

# GET /car/stat => 가격의 총합/평균 구하기
@app.route("/car/stat", methods=["GET"])
def get_car_stat():
    sql = "SELECT sum(price), avg(price) FROM car"
    cursor.execute(sql)
    result = cursor.fetchall()

    # 현재 작성한 코드의 한가지 아쉬운 점이 있다
    # 상태 ON_SALE / ON_RESERVATION가 나중에는 늘어날 수도 있음
    # on_sale_count_sql = "SELECT count(id) FROM car WHERE state = 'ON_SALE'"
    # cursor.execute(on_sale_count_sql)
    # on_sale_count = cursor.fetchall()
    #
    # on_reservation_count_sql = "SELECT count(id) FROM car WHERE state = 'ON_RESERVATION'"
    # cursor.execute(on_reservation_count_sql)
    # on_reservation_count = cursor.fetchall()

    group_sql = "SELECT state, count(1) from car group by state"
    cursor.execute(group_sql)
    group_result = cursor.fetchall()

    sum = result[0][0]
    average = result[0][1]
    dict = {
        'sum': sum,
        'average': average
        # 'on_sale_count': on_sale_count[0][0],
        # 'on_reservation_count': on_reservation_count[0][0]
    }

    for group in group_result:
        dict[group[0]] = group[1]

    print(dict)
    return jsonify(dict)

# @app.route("/car/count", methods=["GET"])
# def get_car_count():
#     sql = "SELECT count(id) from car where state='ON_SALE'"
#     cursor.execute(sql)
#     result = cursor.fetchall()
#     # print(result)
#     OnSaleNumber = result[0][0]
#
#     sql = "SELECT count(id) from car where state='ON_RESERVATION'"
#     cursor.execute(sql)
#     result = cursor.fetchall()
#     # print(result)
#     OnReservationNumber = result[0][0]
#     # print(OnSaleNumber, OnReservationNumber)
#     dict = {
#         'OnSaleNumber': OnSaleNumber,
#         'OnReservationNumber': OnReservationNumber
#     }
#     return jsonify(dict)

# PUT - 판매중 / 예약중 변경
# 여기서도 두 가지 방법이 있다!
# 1) 우리가 서버에서 car의 id를 가지고 있다
    # select * from car where id = ?; -> car를 가져온 담에
    # 그 car의 state를 확인해요 그리고 state에 따라 다른 state를
    # update car set state='???' where id = ?; 업데이트

    # 1-2) 만약에 ORM을 사용한다면?
    # "ORM 객체 - 테이블 매핑"을 사용하지 않고 있음!
    # Car car = carRepository.findById(id);
    # car.toggle();
# @app.route("/car", methods=["PUT"])
# def update_car():
#     data = request.get_json()
#     car_id = data["id"]
#     read_sql = f"SELECT * FROM car WHERE id = {car_id}"
#     cursor.execute(read_sql) # ((), (), ())  (())
#     car = cursor.fetchall()[0]
#     name = car[1]
#     state = car[5]
#
#     # name = data["name"]
#     # state = data["state"]
#     sql = f"UPDATE car SET name = '{name}', state = '{state}' WHERE id = {car_id}"
#     cursor.execute(sql)
#     db.commit()
#     return "OK"

# 2) API 스펙을 바꿔서 화면에서 id랑 변경되어야 하는 state값을 넘겨줘요
# update car set state='들어온값' where id='들어온값';
@app.route("/car", methods=["PUT"])
def update_car():
    data = request.get_json()
    car_id = data["id"]
    after_state = data["afterState"]
    update_sql = f"UPDATE car SET state = '{after_state}' where id = {car_id}"
    cursor.execute(update_sql) # ((), (), ())  (())
    db.commit()
    return "OK"

if __name__ == '__main__':
    app.run(debug=True, threaded=False)