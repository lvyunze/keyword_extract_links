# from urllib.parse import unquote
# import re
#
# x = "https://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E6%98%93%E6%AC%A1%E5%85%83"
# eachvalue = unquote(x, encoding='utf8')
# try:
#     china_str = re.search('[\u4e00-\u9fa5]+[\u4e00-\u9fa5]', eachvalue).group()
#     print(china_str)
#     if "易次元" == china_str:
#         print("yes")
# except AttributeError:
#     pass
#
#
# data = 'https://weibo.com/u/'
# x = re.search(r"/u/+\d+", data).group()
# print(x)
from main import Start
from ip import proxy_list_new
start = Start()
address_list = [
    # "https://s.weibo.com/weibo?q=%E6%98%93%E6%AC%A1%E5%85%83&Refer=STopic_history",
    "https://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E6%98%93%E6%AC%A1%E5%85%83",
    "https://www.douban.com/group/search?cat=1019&q=%E6%98%93%E6%AC%A1%E5%85%83",
    "https://bcy.net/search/home?k=%E6%98%93%E6%AC%A1%E5%85%83"
]
start.run("易次元", {
    "address_list": address_list
})
