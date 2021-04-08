import json
import requests
from bs4 import BeautifulSoup
import pprint


# 웹사이트 신규 기사 링크 템플릿
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


def send_slack_template(incoming_webhook_url, message):
    payload = {'type': 'mrkdwn', 'text': message}
    message_json = json.dumps(payload)
    requests.post(incoming_webhook_url, data=message_json)


def send_slack_list_template(incoming_webhook_url, list_links, main_message):
    send_slack_template(incoming_webhook_url, main_message)
    for item in list_links:
        message = '- <%s|%s>' % (item[1], item[0])
        send_slack_template(incoming_webhook_url, message)

# datas1 = crawling_template_with_href('http://www.drapt.com/e_sale/index.htm?page_name=esale_news&menu_key=34', 'a.c0000000', 'http://www.drapt.com/e_sale/')
datas1 = crawling_template('https://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=310', "#contents_inner > div > table > tbody > tr > td.subject > a")
pprint.pprint(datas1)

incoming_webhook_url = 'https://hooks.slack.com/services/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'
message = '한성정보기술 아이디어 게시판 입니다.'
send_slack_template(incoming_webhook_url, message)
send_slack_list_template(incoming_webhook_url, datas1, '*신규 기사*')