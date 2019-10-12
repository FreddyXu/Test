import requests
from bs4 import BeautifulSoup
import re

key = '毛泽东'
headers = {"User-Agent": "Chrome/75.0.3770.100 Safari/537.36"}
url = "https://baike.baidu.com/item/" + key


def get_names(key):
    url = "https://baike.baidu.com/item/" + key
    wb_data = requests.get(url=url, headers=headers)
    wb_data.encoding = "UTF-8"
    soup = BeautifulSoup(wb_data.text, 'lxml')
    # head > meta:nth-child(8)
    data = soup.select(
        "body > div.body-wrapper > div.content-wrapper > div > div.main-content > div.basic-info.cmn-clearfix > dl.basicInfo-block.basicInfo-left > dt")
    data2 = soup.select(
        "body > div.body-wrapper > div.content-wrapper > div > div.main-content > div.basic-info.cmn-clearfix > dl.basicInfo-block.basicInfo-left > dd")
    names = [i.get_text() for i in data]
    values = [i.get_text() for i in data2]
    keys = ["本名", "别称", "字号", "别名", "中文名"]
    result = []
    for i in range(len(names)):
        result.append([re.sub(" +", "", names[i]), re.sub("[\n ]", "、", values[i])])
    bc = []
    for r in result:
        find = r[0]
        # print(find)
        if find in keys:
            vs = re.split('[、，等]+', r[1])
            for v in vs:
                if v != '':
                    bc.append(re.sub("[号字又\xa0]", "", v))
    return bc


print(get_names(key))

for b in get_names(key):
    print(b)
# # print('=========================================')
# print(data)
# print(data2)
