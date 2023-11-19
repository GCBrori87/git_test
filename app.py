from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider

import json
import sys

app = Flask(__name__)
# 추가했다!

client = MongoClient('mongodb://test:test@3.106.98.242?authSource=admin',27017)
# client = MongoClient('localhost',27017)
db = client.dbjungle

#####################################################################################
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)

# 위에 정의되 custom encoder 를 사용하게끔 설정한다.
app.json = CustomJSONProvider(app)
# #####################################################################################

# API #1: HTML template 전달
@app.route('/')
def home():
    return render_template('index.html')

# API #2: 휴지통에 버려지지 않은 영화 목록 반환
@app.route('/api/list', methods=['GET'])
def show_movies():
    # client 에서 요청한 정렬 방식이 있는지를 확인합니다. 없다면 기본으로 좋아요 순으로 정렬
    sortMode = request.args.get('sortMode', 'likes')

    if sortMode == 'likes':
        movies = list(db.movies.find({'trashed': False}, {}).sort('likes',-1))
    elif sortMode == 'viewers':
        movies = list(db.movies.find({'trashed': False}, {}).sort('viewers',-1))
    elif sortMode == 'date':
        movies = list(db.movies.find({'trashed': False}, {}).sort([('open_year',-1),('open_month',-1),('open_day',-1)]))
    else:
        return jsonify({'result': 'failure'})
    return jsonify({'result': 'success', 'movies_list': movies})

# API #3: 휴지통에 버려진 영화 목록 반환
@app.route('/api/trash', methods=['GET'])
def show_movies_trash():
    # client 에서 요청한 정렬 방식이 있는지를 확인합니다. 없다면 기본으로 좋아요 순으로 정렬
    sortMode = request.args.get('sortMode', 'likes')

    if sortMode == 'likes':
        movies = list(db.movies.find({'trashed': True}, {}).sort('likes',-1))
    elif sortMode == 'viewers':
        movies = list(db.movies.find({'trashed': True}, {}).sort('viewers',-1))
    elif sortMode == 'date':
        movies = list(db.movies.find({'trashed': True}, {}).sort([('open_year',-1),('open_month',-1),('open_day',-1)]))
    else:
        return jsonify({'result': 'failure'})

    return jsonify({'result': 'success', 'movies_list': movies})

# API #4: 영화에 좋아요 숫자를 하나 올립니다.
@app.route('/api/list/like', methods=['POST'])
def like_movie():
    title_receive = request.form['title_give']

    movie = db.movies.find_one({'title': title_receive})
    # 선택된 movie의 like 에 1을 더해준 new_like 변수 생성
    new_likes = movie['likes'] + 1

    # 선택된 movie의 likes 업데이트
    result = db.movies.update_one({'title': title_receive}, {'$set': {'likes': new_likes}})

    if result.modified_count == 1:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})

# API #5: 영화 휴지통으로보내기
@app.route('/api/list/trash', methods=['POST'])
def trash_movie():
    title_receive = request.form['title_give']
    
    # 선택된 movie를 trshed를 True로 변경
    result = db.movies.update_one({'title': title_receive}, {'$set': {'trashed': True}})

    if result.modified_count == 1:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})

# API #6: 휴지통속 영화 복원
@app.route('/api/list/restore', methods=['POST'])
def restore_Movie():
    title_receive = request.form['title_give']

    result = db.movies.update_one({'title': title_receive}, {'$set': {'trashed': False}})

    if result.modified_count == 1:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})

# API #7: 휴지통속 영화 DB에서 영구삭제
@app.route('/api/list/delete', methods=['POST'])
def delete_Movie():
    title_receive = request.form['title_give']

    result = db.movies.delete_one({'title': title_receive})

    return jsonify({'result': 'success'})    

if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)