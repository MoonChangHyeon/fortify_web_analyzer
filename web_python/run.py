# /fortify_web_analyzer/run.py

from app import create_app, db

app = create_app()

# DB 초기화를 위한 CLI 명령어 추가
@app.cli.command("init-db")
def init_db_command():
    """기존 테이블을 삭제하고 새로 생성합니다."""
    # ✨ 수정: app_context() 안에서 DB 작업을 수행
    with app.app_context():
        db.drop_all()
        db.create_all()
    print("데이터베이스 테이블을 성공적으로 초기화했습니다.")