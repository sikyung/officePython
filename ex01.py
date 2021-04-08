import requests
from bs4 import BeautifulSoup
import pprint
import re

def crawling_template(url, css_selector):
    return_data = list()
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    datas1 = soup.select(css_selector)
    for item in datas1:
        return_data.append(item.get_text())
    return return_data


def crawling_template_with_href(url, css_selector, pre_url):
    return_data = list()
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    datas1 = soup.select(css_selector)
    for item in datas1:
        return_data.append([item.get_text(), pre_url + item['href']])
    return return_data


datas1 = crawling_template('https://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=310', "#contents_inner > div > table > tbody > tr > td.subject > a")
pprint.pprint(datas1)




