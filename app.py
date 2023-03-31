from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
import requests
# 비밀번호 암호화에 이용되는 패키지
import jwt, datetime, hashlib

from bs4 import BeautifulSoup

SECRET_KEY='WETUBE'

app = Flask(__name__)
client = MongoClient('mongodb+srv://chunws:test@chunws.w8zkw9b.mongodb.net/?retryWrites=true&w=majority')
db = client.chunws

@app.route('/')
def home():
    token_receive = request.cookies.get('token')
    if token_receive is not None:
        try:
            # 토큰 받아와서 
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            
            # payload 값 중 id로 유저 정보 찾기
            user_info = db.wetube_user.find_one({'user_id':payload['id']}, {'_id': False})
            
            # 유저 정보 중 nick_name 반환
            nick_name = user_info['nick_name']
            user_id = user_info['user_id']
            return render_template('index.html', status = True, nick_name = nick_name, user_id = user_id)
        
        except jwt.ExpiredSignatureError:
            # 토큰 시간이 만료된 경우
            msg = "로그인 시간이 만료되었습니다."
            return render_template('index.html', statud = False, message = msg)
    
    else:
        return render_template('index.html')

# 로그인
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    
    elif request.method == "POST":
        user_id = request.form['user_id']
        password = request.form['password']
        
        # 비밀번호 암호화
        pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        # 아이디와 비밀번호로 유저 찾기
        result_user = db.wetube_user.find_one({"user_id" : user_id, "password" : pw_hash})

        # 등록된 유저가 맞는 경우, find_one 함수로 인해 아이디 / 비밀번호 일치 여부 모두 확인됨
        if result_user is not None:
            # payload : 유저 정보와 만료 시간을 담고 있는 정보 
            # 시크릿키 : payload 값을 알기 위한 키
            # JWT = payload + 시크릿키 ?
            payload = {
                'id' : user_id,
                # 만료 시간, UTC 기준 로그인한 시간 + 500초간 유효함
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=500)
            }
            
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            return jsonify({'status' : True , 'token' : token})
        
        # 등록된 유저가 아닌 경우
        else:
            return jsonify({'status' : False, 'message' : "아이디 또는 비밀번호가 잘못되었습니다."})


# 회원가입    
@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # register.html 파일에서 보내온 회원가입 정보 수신
        userid_receive = request.form['user_id']
        nickname_receive = request.form['nick_name']
        password1_receive = request.form['password1']
        password2_receive = request.form['password2']
        
        # 비밀번호 암호화 
        pw1_hash = hashlib.sha256(password1_receive.encode('utf-8')).hexdigest()
        
        # db에서 동일한 id 존재 여부 확인
        userid_duplication = db.wetube_user.find_one({"user_id" : userid_receive})
                
        # 동일 id 존재할 때
        if userid_duplication is not None:
            msg = "이미 존재하는 아이디 입니다."
            return jsonify({"status" : False, "message" : msg})
        
        # 비밀번호, 확인용 비밀번호가 일치하지 않을때
        elif password1_receive != password2_receive:
            msg = "비밀번호가 서로 일치하지 않습니다."
            return jsonify({"status" : False, "message" : msg})
        
        # 모든 조건을 만족할 때
        else:
            create_user = {
                "user_id" : userid_receive,
                "nick_name" : nickname_receive,
                "password" : pw1_hash
            }
            
            db.wetube_user.insert_one(create_user)
            msg = "회원가입 성공!"
            
            return jsonify({"status" : True, "message" : msg})
    
    # GET 요청시 회원가입 페이지로 유도
    else:
        return render_template('register.html')


# 마이 페이지 접근 로직
@app.route("/mypage", methods=["GET"])
def mypage():
    token_receive = request.cookies.get('token')
    # 로그인한 사용자만 마이 페이지 접근 버튼이 보이므로, 토큰 값이 없는 경우가 없음, <- home 로직과 다른 부분
    try:
        # 토큰 받아와서 
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        
        # payload 값 중 id로 유저 정보 찾기
        user_info = db.wetube_user.find_one({'user_id':payload['id']}, {'_id': False})
        
        # 유저 정보 중 nick_name 반환, 유저 id 기준 등록 영상 조회를 위해 id 전달
        nick_name = user_info['nick_name']
        user_id = user_info['user_id']
        
        # 유저가 등록한 글 찾아내기
        user_content = db.movies.find({"writer" : user_id}, {"_id" : False, "writer": False})
        return render_template('mypage.html', status = True, nick_name = nick_name, user_id = user_id)
    
    except jwt.ExpiredSignatureError:
        # 토큰 시간이 만료된 경우
        msg = "로그인 시간이 만료되었습니다."
        return render_template('index.html', statud = False, message = msg)


# 영상 평가 등록하는 기능
@app.route("/movie/post", methods=["POST"])
def movie_post():
    
    url_receive = request.form['url_give']
    writer_receive = request.form['writer_give'] # 마이페이지 구현을 위해 작성자 신규 등록
    comment_receive = request.form['comment_give']
    star_receive = request.form['star_give']
    
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    # 여기에 코딩을 해서 meta tag를 먼저 가져와보겠습니다.
    ogtitle = soup.select_one('meta[property="og:title"]')['content']
    ogdesc = soup.select_one('link[itemprop="name"]')['content']
    ogimage = soup.select_one('meta[property="og:image"]')['content']

    # 저장 - 예시
    doc = {
        'title' : ogtitle,
        'desc' : ogdesc,
        'image' : ogimage,
        'writer' : writer_receive,
        'comment' : comment_receive,
        'star' : star_receive,
        'url' : url_receive 
    }
    print(doc)
    db.movies.insert_one(doc)

    return jsonify({'msg':'저장 완료!'})


# 첫 페이지 & 마이페이지 영상 정보 가져오기
@app.route("/movie", methods=["GET", "POST"])
def movie_get():
    
    # 마이페이지 - 특정 유저의 게시글을 볼 때
    if request.method == 'POST':
        writer_receive = request.form['writer_give']
        all_movies = list(db.movies.find({'writer': writer_receive}))
        
    # 여러개 찾기 - 예시 ( _id 값은 제외하고 출력)
    else:
        all_movies = list(db.movies.find({}))

    return jsonify({'result' : dumps(all_movies)})

# 수정하기
@app.route("/movie/update", methods=["PUT"])
def movie_put():
    content_id = request.form['id_give']
    comment_new = request.form['comment_give']

    db.movies.update_one({"_id" : ObjectId(content_id)}, {'$set': {'comment': comment_new}})

    return jsonify({'msg':'수정 완료!'})

# 삭제하기
@app.route("/movie/delete", methods=["DELETE"])
def movie_delete():
        
    # 삭제할 영화의 id를 가져온다.
    id = request.form['id_give']
    
    # 삭제할 영화의 id를 가진 영화를 찾는다.
    db.movies.delete_one({'_id': ObjectId(id)})

    return jsonify({'msg':'삭제 완료!'})

# 영상 세부 정보 보기 - 추가
@app.route("/movie/detail/<string:id>")
def movie_detail(id):
    movie_detail = list(db.movies.find({'_id' : ObjectId(id)}))
    return jsonify({"result" : dumps(movie_detail)})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)