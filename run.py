# /fortify_web_analyzer/run.py

from app import create_app, db

# app/__init__.py 파일의 create_app 함수를 호출하여 app을 생성합니다.
app = create_app()

if __name__ == '__main__':
    # 앱 컨텍스트 안에서 DB 테이블을 생성합니다.
    # (테이블이 이미 존재하면 아무 일도 일어나지 않습니다.)
    with app.app_context():
        db.create_all()
    
    # 디버그 모드로 웹 서버를 실행합니다.
    app.run(debug=True)