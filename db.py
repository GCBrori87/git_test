import random
import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

client = MongoClient('mongodb://test:test@3.106.98.242/?authSource=admin',27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle                      # 'dbjungle'라는 이름의 db를 만듭니다.




if __name__ == '__main__':
    # 기존의 movies 콜렉션을 삭제하기
    db.movies.drop()