# /fortify_web_analyzer/app/log_handler.py

import logging
from app import db
from app.models import Log

class SQLAlchemyLogHandler(logging.Handler):
    def emit(self, record):
        """
        로그 레코드가 발생할 때마다 호출되어 DB에 저장합니다.
        """
        traceback = None
        if record.exc_info:
            traceback = logging.Formatter.formatException(self, record.exc_info)
        
        # ✨ 'level' 대신 'status'를 가져와서 사용합니다. ✨
        # 로그 기록 시 전달된 'status' 값을 가져오고, 없으면 'General'로 기본값 설정
        status = getattr(record, 'status', 'General')
        
        log_entry = Log(
            status=status, # 'level='이 아닌 'status='를 사용
            message=record.getMessage(),
            traceback=traceback
        )
        db.session.add(log_entry)
        db.session.commit()