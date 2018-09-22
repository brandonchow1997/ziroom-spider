import requests
from lxml import etree


def get_index():
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/47.0.2526.108 Safari/537.36 2345Explorer/8.8.0.16453 '
    }
    url = 'http://sh.ziroom.com/z/nl/z1.html'
    response = requests.get(url, headers=header)
    return response.text


def parse_index(html):
    url_list = []
    name_list = []
    data = etree.HTML(html)
    items = data.xpath('//*[@id="selection"]/div/div/dl[2]/dd/ul/li[position()>1]')
    for item in items:
        href = item.xpath('./span/a/@href')
        name = item.xpath('./span/a/text()')
        # print(href[0].replace('//', ''))
        url_list.append(href[0].replace('//', 'http://'))
        name_list.append(name[0])
    # print(url_list)
    return url_list, name_list


def districts():
    html = get_index()
    list = parse_index(html)
    return list


if __name__ == '__main__':
    districts()