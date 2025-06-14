# /fortify_web_analyzer/app/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import logging
# ✨ 수정: RotatingFileHandler는 더 이상 필요 없으므로 삭제해도 됩니다.
# from logging.handlers import RotatingFileHandler

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # uploads 폴더 자동 생성
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    db.init_app(app)

    from app.routes import bp as main_blueprint
    app.register_blueprint(main_blueprint)

    # --- ✨ 로깅 설정을 아래와 같이 수정합니다 ✨ ---
    if not app.debug and not app.testing:
        from app.log_handler import SQLAlchemyLogHandler

        # DB 핸들러를 추가합니다.
        db_handler = SQLAlchemyLogHandler()
        db_handler.setLevel(logging.INFO)
        app.logger.addHandler(db_handler)
        
        app.logger.setLevel(logging.INFO)
        
        # --- ✨ 문제의 원인이었던 이 한 줄을 삭제(또는 주석 처리)합니다. ---
        # app.logger.info('Fortify 분석기 시작 (DB 로거 사용)')

    return app

from app import models