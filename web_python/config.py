# /fortify_web_analyzer/config.py

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# .env 파일에서 환경 변수를 로드합니다.
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Flask 앱의 보안을 위한 시크릿 키
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-secret-key'

    # .env 파일에서 MariaDB 연결 정보를 읽어옵니다.
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_NAME = os.environ.get('DB_NAME')
    DB_PORT = '3306'

    # SQLAlchemy 설정
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 280

    # 업로드 폴더 설정
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')