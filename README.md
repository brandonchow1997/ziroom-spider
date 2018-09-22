# 自如租房爬虫
使用selenium无头浏览器爬取上海房源信息。
#爬取结果
![result](https://github.com/brandonchow1997/ziroom-spider/blob/master/result.png)
# 数据分析结果
上海各区合租均价

![合租均价](https://github.com/brandonchow1997/ziroom-spider/blob/master/上海各区合租均价.png)

上海各区整租均价

![整租均价](https://github.com/brandonchow1997/ziroom-spider/blob/master/上海各区整租均价.png)

上海各区房源均价

![整租均价](https://github.com/brandonchow1997/ziroom-spider/blob/master/上海各区房源均价.png)

词云

![整租均价](https://github.com/brandonchow1997/ziroom-spider/blob/master/echarts.png)

# 环境依赖
Python3.6,MongoDB,tesseract
# 库依赖
PIL,pytesseract（提前安装好tesseract）,tqdm（进度条）,retrying（重试）

# 爬虫原理

1.根据页面顶部的区域，分别获取每个区的链接，放入list中。

![步骤1](https://github.com/brandonchow1997/ziroom-spider/blob/master/district.png)
2.遍历区链接list，首先获取总页面数，得知需要爬取的页面总数。

![步骤2](https://github.com/brandonchow1997/ziroom-spider/blob/master/3.png)

3.遍历每页内每个item中的房源标题、房源面积详情信息、距离地铁站的距离等信息，并根据爬取的区名，添加上返回的区字段。并用正则，提取出房屋标题中的房源类型（整租/合租）

![步骤3](https://github.com/brandonchow1997/ziroom-spider/blob/master/2.png)

4.重点爬取价格部分。自如的反爬虫机制，无法在页面内直接获取价格信息。

![步骤4](https://github.com/brandonchow1997/ziroom-spider/blob/master/1.png)

5.因此需要将页面中随机生成的含有0-9数字的图片下载到本地，通过tesseract分别识别每一个数字。

![步骤5](https://github.com/brandonchow1997/ziroom-spider/blob/master/pic.png)

6.识别后便可以通过爬取得到的style属性值得知偏移量，分别确定每个数字，获取最终的房价。

7.存储到MongoDB中。
