import requests
from lxml import etree
import time
from tqdm import tqdm
from retrying import retry
import random
import re
import save_to_mongo
# 接入selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# 接入光学识别库
import pytesseract
from PIL import Image

# -----浏览器初始化
print('正在初始化无头Chrome浏览器...')
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在的报错
chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
# 添加代理 proxy
# chrome_options.add_argument('--proxy-server=http://' + proxy)
browser = webdriver.Chrome(chrome_options=chrome_options)
print('浏览器初始化完毕')
print('-' * 20)


# ------------------


# ---------------获取总页面数
# 每次重试等待两秒
@retry(wait_fixed=2000)
def get_page_num(url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/47.0.2526.108 Safari/537.36 2345Explorer/8.8.0.16453 '
    }
    response = requests.get(url, headers=header)
    data = etree.HTML(response.text)
    try:
        pages = data.xpath('//*[@id="page"]/span[2]/text()')[0]
        final_page = re.search(r"\d+", pages).group()
        return final_page
    except Exception:
        pages = data.xpath('//*[@id="page"]/span[1]/text()')[0]
        final_page = re.search(r"\d+", pages).group()
        return final_page


# -----------------------------


# -------------------获取页面
# 每次重试等待两秒
@retry(wait_fixed=2000)
def get_page(raw_url, page):
    """
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/47.0.2526.108 Safari/537.36 2345Explorer/8.8.0.16453 '
    }
    """
    # 构造参数
    # 可更改
    print('正在爬取第', page, '页')
    url = raw_url + '?p=' + str(page)
    # response = requests.get(url, headers=header)
    browser.get(url)
    time.sleep(random.randint(0, 2))
    response = browser.page_source
    return response


# ---------------------------


# --------解析-----------------------
# 每次重试等待两秒
@retry(wait_fixed=2000)
def parse_page(html, district_name, num_list):
    data = etree.HTML(html)
    items = data.xpath('//*[@id="houseList"]/li[@class="clearfix"]')
    for item in items:
        temp_list = []
        price_list = []
        # 初始化空列表
        list_title = item.xpath('./div[2]/h3/a/text()')
        title = ''.join(list_title)
        # print(title)
        house_type = re.search(r"^..", title).group()
        list_area = item.xpath('./div[2]/div/p[1]/span/text()')
        area = ''.join(list_area)
        # print(area)
        list_metro = item.xpath('./div[2]/div/p[2]/span/text()')
        metro = ''.join(list_metro)
        # print(metro)
        # ---------------Price 极其重要
        prices = item.xpath('./div[3]/p[1]/span[position()>1]/@style')
        for item in prices:
            temp_list.append(item.replace("background-position:-", "").replace("px", ""))
        # print(temp_list)
        for number in temp_list:
            price = num_list[int(int(number) / 30)]
            # print(price)
            price_list.append(price)
        # print(temp_list)
        price_final = ''.join(price_list)
        # ---------------Price 极其重要
        print('=' * 40)
        info = {
            'type': house_type,
            'title': title,
            'area': area,
            'metro': metro,
            'price': price_final,
            'district': district_name
        }
        print(info)
        save_to_mongo.save(info)
    time.sleep(random.randint(0, 2))

    # -----------------------------------------------------------


# tesseract获取图片数字列表的方法
def get_image_number(html):
    photo = re.findall('var ROOM_PRICE = {"image":"(//.*?.png)"', html)[0]
    image = requests.get('http:' + photo).content
    f = open('price.png', 'wb')
    f.write(image)
    f.close()
    num = []
    number = pytesseract.image_to_string(Image.open("price.png"),config="-psm 8 -c tessedit_char_whitelist=1234567890")
    for i in number:
        num.append(i)
    return num


"""
# 房价映射字典
price_dict = {
    'background-position:-210px': '9',
    'background-position:-0px': '4',
    'background-position:-240px': '7',
    'background-position:-90px': '5',
    'background-position:-60px': '3',
    'background-position:-120px': '1',
    'background-position:-270px': '6',
    'background-position:-30px': '0',
    'background-position:-180px': '2',
    'background-position:-150px': '8',
}
"""

if __name__ == '__main__':
    i = 0
    print('正在初始化地区模块...')
    import ziru_district
    url_items = ziru_district.districts()[0]
    name_items = ziru_district.districts()[1]
    print('地区模块初始化完毕')
    print('-' * 20)
    time.sleep(1)
    # ---------------------
    for url_item in url_items:
        url = url_item
        end = get_page_num(url)
        print('...')
        print('正在爬取 {name} 的房源'.format(name=name_items[i]))
        print('共有', end, '页')
        for page in tqdm(range(1, int(end))):
            html = get_page(url, page)
            # 获取随机数字列表
            num_list = get_image_number(html)
            # print(num_list)
            parse_page(html, name_items[i], num_list)
        i = i + 1
