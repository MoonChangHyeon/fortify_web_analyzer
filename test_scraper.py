# /fortify_web_analyzer/test_scraper.py

import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def test_single_language_scrape():
    """
    'Java' 언어 하나에 대해서만 vulncat 사이트를 스크레이핑하여
    결과를 터미널에 출력하는 테스트 함수.
    """
    lang_name = "Java/JSP"
    base_url = f"https://vulncat.fortify.com/ko/weakness?codelang={lang_name}"
    
    print("--- 테스트 시작: 웹 드라이버 설정 ---")
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        print("--- 웹 드라이버 설정 완료 ---")
    except Exception as e:
        print(f"오류: 웹 드라이버 설정 실패. {e}")
        return

    print(f"'{lang_name}'의 첫 페이지로 접속합니다: {base_url}")
    driver.get(base_url)

    all_scraped_rules = []
    page_count = 1

    while True:
        try:
            print(f"\n--- 페이지 {page_count} 처리 중 ---")
            
            # 1. [명시적 대기] 규칙 목록의 첫번째 항목이 나타날 때까지 최대 10초 기다립니다.
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list-group-item")))
            print("규칙 목록 로딩 완료.")

            # 2. 현재 페이지의 규칙 이름들을 수집합니다.
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            rule_list_container = soup.find('div', class_='list-group')
            rule_links = rule_list_container.find_all('a', class_='list-group-item') if rule_list_container else []
            
            if not rule_links:
                print("현재 페이지에서 규칙을 찾지 못했습니다. 스크레이핑 종료.")
                break

            current_page_rules = [link.get_text(strip=True) for link in rule_links]
            all_scraped_rules.extend(current_page_rules)
            
            print(f"페이지 {page_count}에서 {len(current_page_rules)}개의 규칙 발견:")
            for rule in current_page_rules:
                print(f"  - {rule}")

            # 3. '다음(>)' 버튼을 찾아서 클릭합니다.
            pagination_nav = driver.find_element(By.CSS_SELECTOR, "ul.pagination")
            # 'aria-label="Next"' 속성을 가진 'a' 태그를 찾습니다.
            next_button = pagination_nav.find_element(By.CSS_SELECTOR, "a[aria-label='Next']")
            
            # 'disabled' 클래스가 있으면 마지막 페이지이므로 루프를 중단합니다.
            if 'disabled' in next_button.find_element(By.XPATH, "..").get_attribute("class"):
                print("\n마지막 페이지입니다. 스크레이핑 종료.")
                break
            
            print("\n'다음' 버튼 클릭...")
            next_button.click()
            page_count += 1

        except TimeoutException:
            print("오류: 페이지 로딩 시간이 초과되었습니다. 스크레이핑 종료.")
            break
        except NoSuchElementException:
            print("\n'다음' 버튼을 더 이상 찾을 수 없습니다. 마지막 페이지입니다. 스크레이핑 종료.")
            break
        except Exception as e:
            print(f"오류: 페이지 {page_count} 처리 중 문제가 발생했습니다. ({e})")
            break
            
    driver.quit()

    print("\n" + "="*40)
    print(f"최종 스크레이핑 결과: 총 {len(all_scraped_rules)}개의 규칙을 수집했습니다.")
    print("="*40)


if __name__ == '__main__':
    test_single_language_scrape()