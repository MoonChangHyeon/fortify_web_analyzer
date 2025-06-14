# /fortify_web_analyzer/app/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# db 객체를 먼저 전역적으로 생성합니다.
db = SQLAlchemy()

def create_app(config_class=Config):
    """
    Flask app을 생성하고 설정한 뒤 반환하는 'Application Factory' 함수.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 업로드 폴더가 없으면 생성합니다.
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    # db 객체를 app과 연결(초기화)합니다.
    db.init_app(app)

    # routes.py에 정의된 라우트(블루프린트)들을 앱에 등록합니다.
    from app.routes import bp as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

# 다른 파일에서 'from app import models'를 할 수 있도록,
# 순환 참조를 피하기 위해 가장 마지막에 import 합니다.
from app import models