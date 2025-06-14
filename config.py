# /fortify_web_analyzer/config.py
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # MariaDB 연결 정보
    DB_USER = 'fortify'
    DB_PASSWORD = 'Fortify!234'
    DB_HOST = 'localhost'
    DB_PORT = '3306'
    DB_NAME = 'fortify_analyzer'

    # SQLAlchemy 설정
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- ✨ 이 한 줄을 추가해주세요! ---
    SQLALCHEMY_POOL_RECYCLE = 280 # 초 단위, 280초(약 4분 40초)마다 연결을 재활용

    # Flask 앱의 다른 설정들
    SECRET_KEY = 'a-very-secret-key-for-flash-messages'
    
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')