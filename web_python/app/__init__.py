# /fortify_web_analyzer/app/__init__.py

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # uploads 폴더 자동 생성
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    db.init_app(app)

    # ✨ 수정: 블루프린트 등록을 로거 설정보다 먼저 수행
    from app.routes import bp as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # ✨ 수정: 로깅 설정을 create_app 함수의 맨 마지막으로 이동
    if not app.debug and not app.testing:
        from app.log_handler import SQLAlchemyLogHandler

        db_handler = SQLAlchemyLogHandler()
        db_handler.setLevel(logging.INFO)
        app.logger.addHandler(db_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Fortify 분석기 시작 (DB 로거 사용)')

    return app

from app import models