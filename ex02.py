# 크롬 브라우저를 띄우기 위해, 웹드라이버를 가져오기
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

# 크롬 드라이버로 크롬을 실행한다.
driver = webdriver.Chrome('D:/chromedriver.exe')
try:
    # 입찰정보 검색 페이지로 이동
    driver.get('http://www.g2b.go.kr:8101/ep/tbid/tbidFwd.do')

    # 업무 종류 체크
    task_dict = {'용역': 'taskClCds5', '민간': 'taskClCds20', '기타': 'taskClCds4'}
    for task in task_dict.values():
        checkbox = driver.find_element_by_id(task)
        checkbox.click()

    # 검색어
    query = '채용'
    # id값이 bidNm인 태그 가져오기
    bidNm = driver.find_element_by_id('bidNm')
    # 내용을 삭제 (버릇처럼 사용할 것!)
    bidNm.clear()
    # 검색어 입력후 엔터
    bidNm.send_keys(query)
    bidNm.send_keys(Keys.RETURN)
    # 검색 조건 체크
    option_dict = {'검색기간 1달': 'setMonth1_1', '입찰마감건 제외': 'exceptEnd', '검색건수 표시': 'useTotalCount'}
    for option in option_dict.values():
        checkbox = driver.find_element_by_id(option)
        checkbox.click()
    # 목록수 100건 선택 (드롭다운)
    recordcountperpage = driver.find_element_by_name('recordCountPerPage')
    selector = Select(recordcountperpage)
    selector.select_by_value('100')
    # 검색 버튼 클릭
    search_button = driver.find_element_by_class_name('btn_mdl')
    search_button.click()
    # 검색 결과 확인
    elem = driver.find_element_by_class_name('results')
    div_list = elem.find_elements_by_tag_name('div')
    # 검색 결과 모두 긁어서 리스트로 저장
    results = []
    for div in div_list:
        results.append(div.text)
        a_tags = div.find_elements_by_tag_name('a')
        if a_tags:
            for a_tag in a_tags:
                link = a_tag.get_attribute('href')
                results.append(link)
    # 검색결과 모음 리스트를 12개씩 분할하여 새로운 리스트로 저장
    result = [results[i * 12:(i + 1) * 12] for i in range((len(results) + 12 - 1) // 12)]
    # 결과 출력
    print(result)
except Exception as e:
    # 위 코드에서 에러가 발생한 경우 출력
    print(e)
finally:
    # 에러와 관계없이 실행되고, 크롬 드라이버를 종료
    driver.quit()