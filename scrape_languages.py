# /fortify_web_analyzer/scrape_languages.py

import os
import sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote

# --- Flask 앱의 DB 설정을 가져오기 위한 설정 ---
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)

from app import create_app, db
from app.models import Rule, Language

app = create_app()
app.app_context().push()

# --- 스크레이핑 설정 ---
LANGUAGES_STRING = "ABAP ActionScript Apex Bicep C#/VB.NET/ASP.NET C/C++ COBOL ColdFusion Dart Docker Golang HCL JSON Java/JSP JavaScript/TypeScript Kotlin Objective-C PHP PLSQL/TSQL Python Ruby Scala Solidity Swift Universal VisualBasic/VBScript/ASP YAML"
LANGUAGES_TO_SCRAPE = LANGUAGES_STRING.split(' ')
BASE_URL = "https://vulncat.fortify.com/ko/weakness"


def scrape_and_store_data():
    print("--- 웹 드라이버 설정 시작 ---")
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        print("--- 웹 드라이버 설정 완료 ---")
    except Exception as e:
        print(f"오류: 웹 드라이버 설정에 실패했습니다. ({e})")
        return

    for lang_name in LANGUAGES_TO_SCRAPE:
        try:
            print(f"\n--- '{lang_name}' 언어 처리 시작 ---")
            
            lang_obj = Language.query.filter_by(name=lang_name).first()
            if not lang_obj:
                lang_obj = Language(name=lang_name)
                db.session.add(lang_obj)
                db.session.commit()
                print(f"'{lang_name}' 언어를 DB에 새로 추가했습니다.")

            # --- 페이징 처리를 위한 루프 ---
            page_offset = 1
            total_new_links = 0
            while True:
                encoded_lang_name = quote(lang_name, safe='')
                if page_offset == 1:
                    target_url = f"{BASE_URL}?codelang={encoded_lang_name}"
                else:
                    target_url = f"{BASE_URL}?codelang={encoded_lang_name}&po={page_offset}"

                print(f"GET: Page {page_offset} -> {target_url}")
                driver.get(target_url)
                # 자바스크립트가 컨텐츠를 로드할 시간을 줍니다.
                time.sleep(3)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                rule_list_container = soup.find('div', class_='list-group')
                rule_links = rule_list_container.find_all('a', class_='list-group-item') if rule_list_container else []

                if not rule_links:
                    print(f"Page {page_offset}에서 더 이상 규칙을 찾을 수 없습니다. '{lang_name}' 언어 처리 종료.")
                    break

                newly_added_count = 0
                for link in rule_links:
                    rule_name = link.get_text(strip=True)
                    rule_obj = Rule.query.filter_by(rule_name=rule_name).first()
                    
                    if rule_obj and lang_obj not in rule_obj.languages:
                        rule_obj.languages.append(lang_obj)
                        newly_added_count += 1
                
                db.session.commit()
                if newly_added_count > 0:
                    print(f"Page {page_offset}: 새로운 규칙-언어 연결 {newly_added_count}개를 DB에 추가했습니다.")
                
                total_new_links += newly_added_count
                page_offset += 1

            if total_new_links > 0:
                 print(f"'{lang_name}' 언어에 대해 총 {total_new_links}개의 새로운 연결을 추가했습니다.")

        except Exception as e:
            print(f"오류: '{lang_name}' 처리 중 문제가 발생했습니다. ({e})")
            db.session.rollback()

    driver.quit()
    print("\n--- 모든 작업 완료 ---")


if __name__ == '__main__':
    if not Rule.query.first():
        print("오류: DB에 규칙(Rule) 데이터가 없습니다.")
        print("웹 앱의 '/upload' 페이지에서 externalmetadata.xml 파일을 먼저 업로드해주세요.")
    else:
        scrape_and_store_data()