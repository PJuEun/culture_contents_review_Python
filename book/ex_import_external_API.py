import pymysql
import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
db = pymysql.connect(host='localhost', port=3306, user='root', password='1234', db='library', charset='utf8')
cursor = db.cursor()

@app.route("/index", methods=["GET"])
def main_page():
    return render_template("book_search.html")

#
# API = 약속
# 외부 API를 사용한다는 것은 외부 (네이버 / 카카오 / 구글 / API 제공업체) 에서 정해둔 "약속"에 따라
# 우리가 API를 호출해야한다는 것을!
# $.ajax({type : "GET", url: ""})

# 유저에게 검색어를 받아서, 가장 연관성 높은 책 3권만 추천!
# GET /book.recommend?query=문자열
# 그럼 우리는 여기서 받은 문자열 그대로~ Naver API를 사용해서 결과를 가져오고
# 그 결과 중 3개만 가져와서 다시 반환
# 클라이언트 ---> python 서버 ---> Naver API
# Naver API ---> python 서버 받아서 가공 ---> 클라이언트

@app.route("/book/recommend", methods=["GET"])
def recommend_book():
    keyword = request.args["keyword"]
    headers = {
        "X-Naver-Client-Id": "hSJmKPBYYv3pj32JZCGV",
        "X-Naver-Client-Secret": "LZHsBSVHHv"
    }
    # keyword = "부동산"
    result = requests.get(f"https://openapi.naver.com/v1/search/book.json?query={keyword}", headers=headers)
    json = result.json()
    # json["items"][0:3] # 이건 리스트

    return_result = []
    for item in json["items"][0:3]:
        return_result.append({
            "title": item["title"],
            "thumbnail": item["image"]
        })

    return jsonify(return_result)


if __name__ == '__main__':
    app.run(debug=True, threaded=False)
