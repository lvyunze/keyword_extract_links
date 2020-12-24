from functools import lru_cache
import httpx
from fake_useragent import UserAgent
ua = UserAgent()


@lru_cache()
def get_html(url):
    headers = {'user-agent': ua.random}
    r = httpx.get(url, headers=headers)
    return r.text


# @lru_cache()
# def send_request():
#     url_list = [
#         "https://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E6%98%93%E6%AC%A1%E5%85%83",
#         "https://s.weibo.com/weibo?q=%E6%98%93%E6%AC%A1%E5%85%83&Refer=STopic_history"
#         "https://www.douban.com/group/search?cat=1019&q=%E6%98%93%E6%AC%A1%E5%85%83",
#         "https://bcy.net/search/home?k=%E6%98%93%E6%AC%A1%E5%85%83"
#     ]
#     html_list = []
#     for url in url_list:
#         html = get_html(url)
#         html_list.append(html)
#
#
# if __name__ == '__main__':
#     data = get_html('https://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E6%98%93%E6%AC%A1%E5%85%83')
#     print(type(data))
