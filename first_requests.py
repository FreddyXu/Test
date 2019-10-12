import requests
from bs4 import BeautifulSoup
import re

headers = {"User-Agent": "Chrome/75.0.3770.100 Safari/537.36"}
keys = ['清华大学', "北京大学", "四川大学", "南京大学", "毛泽东", "李白"]


def get_names(key):
    url = "https://baike.baidu.com/item/" + key
    wb_data = requests.get(url=url, headers=headers)
    wb_data.encoding = "UTF-8"
    soup = BeautifulSoup(wb_data.text, 'lxml')
    # head > meta:nth-child(8)
    data = soup.select(
        # body > div.body-wrapper.feature.feature_small.collegeSmall > div.content-wrapper > div > div.main-content > div.main_tab.main_tab-defaultTab.curTab > div.basic-info.cmn-clearfix > dl.basicInfo-block.basicInfo-left
        # body > div.body-wrapper > div.content-wrapper > div > div.main-content > div.basic-info.cmn-clearfix > dl.basicInfo-block.basicInfo-left
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
        if find in keys:
            vs = re.split('[、，等]', r[1])
            for v in vs:
                if len(v):
                    bc.append(re.sub("[号字又\xa0]", "", v))
    return bc


for key in keys:
    url = "https://baike.baidu.com/item/" + key
    wb_data = requests.get(url=url, headers=headers)
    result = get_names(key)
    wb_data.encoding = "UTF-8"
    soup = BeautifulSoup(wb_data.text, 'lxml')
    data = soup.select("head > meta")
    jc = re.findall('[简别又][称号]“[\u4E00-\u9FA5]+”|[字号][\u4E00-\u9FA5]+|尊称为“[\u4E00-\u9FA5]+”|誉为“[\u4E00-\u9FA5]+”'
                    '', str(data))
    for i in jc:
        su = re.sub('[简别又称号字誉为尊称为“”]+', '', i)
        result.append(su)
    # lis = "|".join([re.sub('[简别又称号字誉为尊称为“”]', '', i) for i in jc])
    print(key + ":" + str(set(result)))

# for item in data:
#     result = {
#         'title': item.get_text(),
#         'link': item.get('href')
#     }
#     print(result)
# print(soup.head)】
