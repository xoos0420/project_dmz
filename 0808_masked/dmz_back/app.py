import os
import pymysql
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import DAO
import DTO


# 환경변수로 중요한 데이터 빼놓은 부분

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#db와연동 확인
try:
    connect = pymysql.connect(host="svc.sel4.cloudtype.app", user="root", password="1234", db="dmz",port=30302)
    print("MariaDB에 연결")
    cur = connect.cursor()

except pymysql.Error as e:
    print("MariaDB 연결에 실패하였습니다.")
    print(e)

class Input_sentence(BaseModel):
    input_sentence: str

#db와연동 확인
@app.get("/")
async def root():
    print('랜덤요청 들어옴')
    random_word1,random_word2,random_word3 = DAO.random_word(cur)
    return JSONResponse(content={'random1': random_word1,
                                'random2': random_word2,
                                'random3': random_word3})

@app.post('/request')
async def predict(input_sentence: Input_sentence):
    print('요청받음')
    value = input_sentence.input_sentence
    print(value)
    result_word,result_mean,result_sentence = DTO.main(value,cur)
    return JSONResponse(content={'word': result_word,
                                'mean': result_mean,
                                'sentence': result_sentence})
#랜덤 3개 출력해줄 것 
@app.post('/random')
async def predict(input_sentence: Input_sentence):
    value = input_sentence.input_sentence
    print('랜덤 버튼 요청받은 값')
    print(value)
    result = DAO.search_db(value,cur)
    return JSONResponse(content={'word': result[0],
                                'mean' : result[1],
                                'sentence': result[2]})




