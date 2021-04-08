from selenium import webdriver  # selenium 프레임 워크에서 webdriver 가져오기

url = 'http://naver.com'        # 접속할 웹 사이트 주소 (네이버)
driver = webdriver.Chrome('D:/chromedriver.exe')  # 크롬 드라이버로 크롬 켜기
driver.get(url)                 # 저장한 url 주소로 이동