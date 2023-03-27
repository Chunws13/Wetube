from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
import re

# 비밀번호 암호화에 이용되는 패키지
import jwt, datetime, hashlib


app = Flask(__name__)
client = MongoClient('mongodb+srv://chunws:test@chunws.w8zkw9b.mongodb.net/?retryWrites=true&w=majority')
db = client.chunws

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    
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
            return render_template('register.html', message = msg)
        
        # 비밀번호, 확인용 비밀번호가 일치하지 않을때
        elif password1_receive != password2_receive:
            msg = "비밀번호가 서로 일치하지 않습니다."
            return render_template('register.html', message = msg)
        
        # 모든 조건을 만족할 때
        else:
            create_user = {
                "user_id" : userid_receive,
                "nick_name" : nickname_receive,
                "password" : pw1_hash
            }
            
            db.wetube_user.insert_one(create_user)
            msg = "회원가입 성공!"
        
            return render_template('/login.html', message=msg)
    
    # GET 요청시 회원가입 페이지로 유도
    else:
        return render_template('register.html')
if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)