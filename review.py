# 다음과 같은 정보를 입력할 수 있습니다.
# - 제목 / 날짜 / 유형 (영화, 소설, 관람) / 평점 1~5 / 후기
# 평점과 후기는 수정할 수 있습니다.
# 우리가 지금까지 입력했던 정보를 최신 순으로 확인할 수 있어야 합니다.
# 각 유형별로 아래 정보를 확인할 수 있어야 합니다.
# - 총 몇 편의 문화 컨텐츠 후기를 등록했는가?
# - 평균 평점은 몇 점인가?
# - 예를 들어, 영화 5개 (평균 : 2.5) / 소설 3개 (평균 3.0) / 관람 2개 (평균 4.0) 라는 정보를 확인할 수 있어야 한다.

# id : id [int[10]] REIMARY KEY
# 제목 : name [varchar[20]]
# 날짜 : date [DATE]
# 유형(영화, 소설, 관람) : type [varchar[10]
# 평점 1~5 : grade int[10]
# 후기 : review varchar[255]

# GET(데이터 보여주기) / POST(데이터 집어넣기) / PUT(데이터 수정하기/평점,후기)
# path : /review
# id, name(제목), date(날짜), type(유형:영화/소설/관람), grade(평점), review(후기)

# 만들어야 할 3가지 기능
# 저장 기능 -> 조회 기능 -> 수정 기능

# 화면
# 후기를 등록하는 화면
# 후기 목록을 보여주는 화면
# 평점과 후기 수정하는 화면 (나중에 시간남으면 추가해보기)

import pymysql
from flask import Flask, jsonify, request, render_template
from datetime import datetime

app = Flask(__name__)
db = pymysql.connect(host='localhost', port=3306, user='root', password='1234', db='review', charset='utf8')
cursor = db.cursor()


# 후기를 등록하는 화면
@app.route("/review_save", methods=["GET"])
def review_save_page():
    return render_template('review_save.html')

# 후기 목록을 보여주는 화면
@app.route("/review_list", methods=["GET"])
def review_list_page():
    return render_template('review_list.html')

# 후기를 수정하는 화면
@app.route("/review_update", methods=["GET"])
def review_update_page():
    return render_template('review_update.html')

# POST : 데이터 집어넣기
@app.route("/review", methods=["POST"])
def save_review():
    data = request.get_json()
    name = data["name"]
    date = get_today()
    type = data["type"]
    grade = data["grade"]
    review = data["review"]

    sql = f"INSERT INTO review (name, date, type, grade, review) VALUES('{name}', '{date}', '{type}', {grade}, '{review}')"
    cursor.execute(sql)
    db.commit()
    return "OK"

def get_today():
    today = datetime.today()
    return today.strftime("%Y-%m-%d")


# GET : 데이터 보여주기
@app.route("/review", methods=["GET"])
def get_review():
    sql = "select * from review order by id desc"
    cursor.execute(sql)
    results = cursor.fetchall()
    result_dict = []

    for result in results:
        result_dict.append({
            "id": result[0],
            "name": result[1],
            "date": result[2].strftime("%Y-%m-%d"),
            "type" : result[3],
            "grade" : result[4],
            "review" : result[5]
        })
    return jsonify(result_dict)

# GET : 총 갯수, 평균 평점
# - 영화 5개 (평균 : 2.5) / 소설 3개 (평균 3.0) / 관람 2개 (평균 4.0)
@app.route("/review/stat", methods=["GET"])
def get_review_stat():

    group_sql = "SELECT type, count(1), round(avg(grade), 1) from review group by type"
    cursor.execute(group_sql)
    group_result = cursor.fetchall()

    dict = { }
    for group in group_result:
        dict[group[0]] = [group[1], group[2]]
        # dict[group[0]] = [group[0], group[1], group[2]]

    return jsonify(dict)

# PUT : 데이터 수정하기/평점(grade),후기(review)
@app.route("/review", methods=["PUT"])
def update_review():
    data = request.get_json()
    review_id = data["id"]
    grade = data["grade"]
    review = data["review"]
    sql = f"UPDATE review SET grade = {grade}, review = '{review}' where id = {review_id}"
    cursor.execute(sql)
    db.commit()
    return "OK"


if __name__ == '__main__':
    app.run(debug=True, threaded=False)