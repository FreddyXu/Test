import requests
from bs4 import BeautifulSoup
import re
from lxml import etree

headers = {"User-Agent": "Chrome/75.0.3770.100 Safari/537.36"}
li = []
for r in range(18):
    # '{0}\'s age is {1}'.format(name,age)
    url = "http://baike.baidu.com/fenlei/%E5%AE%98%E5%91%98?limit=30&index={0}&offset=30".format(r)
    wb_data = requests.get(url=url, headers=headers).content.decode("UTF-8")
    html = etree.HTML(wb_data)
    html_data = html.xpath('/html/body/div/div/div/div/div/div/ul/li/div/a')
    # html_data1 = html.xpath('')
    for i in html_data:
        te = i.text
        if te is not None:
            if "·" not in te and len(te) <= 3:
                li.append(te)

for j in li:
    print(j)
