# /fortify_web_analyzer/app/log_handler.py

import logging
from flask import has_request_context

class SQLAlchemyLogHandler(logging.Handler):
    def emit(self, record):
        """
        로그 레코드가 발생할 때마다 호출되어 DB에 저장합니다.
        웹 요청 컨텍스트 안에서만 DB 작업을 수행합니다.
        """
        # 웹 요청이 없는 경우(예: flask init-db 실행 시)에는 DB에 로그를 남기지 않음
        if not has_request_context():
            return

        from app import db
        from app.models import Log

        traceback = None
        if record.exc_info:
            traceback = logging.Formatter.formatException(self, record.exc_info)
        
        status = getattr(record, 'status', 'General')
        
        log_entry = Log(
            status=status,
            message=record.getMessage(),
            traceback=traceback
        )
        db.session.add(log_entry)
        db.session.commit()