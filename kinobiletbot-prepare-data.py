# encoding: utf-8

import urllib.request
import json
from lxml import html
import pprint
import re
import os


def remove_emoji(data):
    """
    去除表情
    :param data:
    :return:
    """
    if not data:
        return data
    if not isinstance(data, str):
        return data
    try:
    # UCS-4
        patt = re.compile(u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])')
    except re.error:
    # UCS-2
        patt = re.compile(u'([\u2600-\u27BF])|([\uD83C][\uDF00-\uDFFF])|([\uD83D][\uDC00-\uDE4F])|([\uD83D][\uDE80-\uDEFF])')
    return patt.sub('', data)


url = "http://pobedafilm.ru/card/?d=2017-05-28"
page = html.fromstring(urllib.request.urlopen(url).read())

info = {}

for movie_item in page.xpath("//ul[*]"):
    link_tag = movie_item.xpath(".//a")[0]
    image_tag = link_tag.xpath(".//div")[0].get("style") 
    nobr_tags = movie_item.xpath(".//nobr[*]")

    url = "http://pobedafilm.ru/card/{}".format(link_tag.get("href"))
    image_link = 'http://{}'.format(image_tag[image_tag.find("url('//")+7:image_tag.find("');")])

    title_tag = movie_item.xpath(".//h2")[0]                                    
    title_text = title_tag.xpath(".//a")[0].text                                
    title_extended_text = remove_emoji(' '.join(title_tag.xpath(".//text()"))).strip()[len(title_text):].strip()

    if title_text not in info.keys():
        info[title_text] = []

    sessions = []

    for time_item in nobr_tags:
        time_text = time_item.xpath(".//a")[0].text
        hall = time_item.xpath(".//a")[0].get("data-hall")
        time_link = "http://pobedafilm.ru/card/{}&g=1".format(time_item.xpath(".//a")[0].get("href"))
        price = time_item.xpath(".//text()")[1].strip()[1:].split(" ")[0]

        sessions.append({
            'time': time_text,
            'url': time_link,
            'price': price,
            'hall': hall
        })

    info[title_text].append({                                                   
        'option': title_extended_text,                                          
        'url': url,                                                             
        'image_link': image_link,                                               
        'sessions': sessions                                                        
    })

info_list = []
for k, v in info.items():
    info_list.append({k: v})

print(pprint.pprint(info))
with open('kinobiletbot.json', 'w') as f:
    json.dump(info_list, f, ensure_ascii=False, indent=4, sort_keys=True)
    #f.write(json.dumps(info))

