
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from datetime import datetime

BASE_URL = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok='
CODES = {0: 'KOSPI', 1: 'KOSDAQ'}
START_PAGE = 1
fields = []
now = datetime.now()
formattedDate = now.strftime("%Y%m%d")


def get_bbb_interest_rate():
    """BBB- 채권 5년 기대수익률을 크롤링하는 함수"""
    try:
        url = 'https://www.kisrating.com/ratingsStatistics/statics_spread.do'
        res = requests.get(url)
        page_soup = BeautifulSoup(res.text, 'lxml')

        table = page_soup.select_one('div.table_ty1')

        # html -> 문자열
        table_html = str(table)

        # pandas의 read_html로 테이블 정보 읽기
        table_df = pd.read_html(table_html)[0]

        table_df.set_index('구분', inplace=True)
        interest_rate = table_df.loc['BBB-', '5년']
        print(interest_rate, type(interest_rate))
        return interest_rate

    except Exception as e:
        return 0


def executor():
    bbb_interest_rate = get_bbb_interest_rate()

    # CODES는 KOSPI, KOSDAQ 모두를 대상으로 유니버스를 구성하고 싶은 경우 사용, 현재는 KOSPI만 대상
    for code in CODES.keys():

        # total_page을 가져오기 위한 requests
        res = requests.get(BASE_URL + str(code) + "&page=" + str(START_PAGE))
        page_soup = BeautifulSoup(res.text, 'lxml')

        # total_page 가져오기
        total_page_num = page_soup.select_one('td.pgRR > a')
        total_page_num = int(total_page_num.get('href').split('=')[-1])

        # 가져올 수 있는 항목명들을 추출
        ipt_html = page_soup.select_one('div.subcnt_sise_item_top')

        # fields라는 변수에 담아 다른 곳에서도 사용할 수 있도록 global 키워드를 붙임
        global fields
        fields = [item.get('value') for item in ipt_html.select('input')]

        # page마다 정보를 긁어오게끔 하여 result에 저장
        result = [crawler(code, str(page)) for page in range(1, total_page_num + 1)]

        # page마다 가져온 정보를 df에 하나로 합침
        df = pd.concat(result, axis=0, ignore_index=True)

        df.to_excel('NaverFinance.xlsx')

        # Naver Finance에서 긁어온 종목들을 바탕으로 유니버스 구성
        # N/A로 값이 없는 필드 0으로 채우기
        mapping = {',': '', 'N/A': '0'}
        df.replace(mapping, regex=True, inplace=True)

        # 1억
        BILLION = 100000000

        df['자본'] = df['자산총계'].astype(float) - df['부채총계'].astype(float)
        df['ROE'] = df['ROE'].astype(float)

        # Naver Finance 데이터 중 상장주식수는 만자리부터 표현하므로 1000을 곱해줌
        df['상장주식수'] = df['상장주식수'].astype(float) * 1000

        # bbb- 채권 5년 기대수익률, https://www.kisrating.com/ratingsStatistics/statics_spread.do
        bbb_expect_return = bbb_interest_rate or 7.9

        # 초과이익
        excess_profit = df['자본'] * BILLION * (df['ROE'] - bbb_expect_return) / 100

        # 적정주가 총가치
        fair_stock_value = df['자본'] * BILLION + df['자본'] * BILLION * (df['ROE'] - bbb_expect_return) / bbb_expect_return

        # 적정주가
        df['적정가'] = fair_stock_value / df['상장주식수']

        # 할인율(10%) 적용 총가치
        discount_10_value = df['자본'] * BILLION + excess_profit * 0.9 / (1 + bbb_expect_return / 100 - 0.9)

        # 할인율(10%) 적용 가격
        df['할인율(10%)적용_적정가'] = discount_10_value / df['상장주식수']

        # 할인율(20%) 적용 총가치
        discount_20_value = df['자본'] * BILLION + excess_profit * 0.8 / (1 + bbb_expect_return / 100 - 0.8)

        # 할인율(20%) 적용 가격
        df['할인율(20%)적용_적정가'] = discount_20_value / df['상장주식수']

        # 최종결과를 엑셀로 내보내기
        df.to_excel('NaverFinance_%s_%s.xlsx' % (CODES[code], formattedDate))


def crawler(code, page):
    # get_universe에서 저장한 항목명들 모음
    global fields

    # naver finance에 전달할 값들을 만듬, fieldIds에 먼저 가져온 항목명들을 전달하면 이에 대한 응답을 준다.
    data = {'menu': 'market_sum',
            'fieldIds': fields,
            'returnUrl': BASE_URL + str(code) + "&page=" + str(page)}

    # requests.get 요청대신 post 요청을 보낸다.
    res = requests.post('https://finance.naver.com/sise/field_submit.nhn', data=data)

    page_soup = BeautifulSoup(res.text, 'lxml')

    # 크롤링할 table html 가져온다. 실질적으로 사용할 부분
    table_html = page_soup.select_one('div.box_type_l')

    # column명을 가공한다.
    header_data = [item.get_text().strip() for item in table_html.select('thead th')][1:-1]

    # 종목명 + 수치 추출 (a.title = 종목명, td.number = 기타 수치)
    inner_data = [item.get_text().strip() for item in table_html.find_all(lambda x:
                                                                          (x.name == 'a' and
                                                                           'tltle' in x.get('class', [])) or
                                                                          (x.name == 'td' and
                                                                           'number' in x.get('class', []))
                                                                          )]

    # page마다 있는 종목의 순번 가져오기
    no_data = [item.get_text().strip() for item in table_html.select('td.no')]
    number_data = np.array(inner_data)

    # 가로x 세로 크기에 맞게 행렬화
    number_data.resize(len(no_data), len(header_data))

    # 한 페이지에서 얻은 정보를 모아 DataFrame로 만들어 리턴
    df = pd.DataFrame(data=number_data, columns=header_data)
    return df


if __name__ == "__main__":
    print('Start!')
    executor()
    print('End')
