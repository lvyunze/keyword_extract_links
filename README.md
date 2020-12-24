> pip install keyword_extract_links

> httpx,fake_useragent must be installed to test before use,but the keyword_extract_Links library is not dependent

```
from keyword_extract_links import extract_links
import httpx
from fake_useragent import UserAgent
ua = UserAgent()


def get_html(url_address):
    headers = {'user-agent': ua.random}
    r = httpx.get(url_address, headers=headers)
    return r.text


url_list = [
              "https://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E6%98%93%E6%AC%A1%E5%85%83",
              "https://s.weibo.com/weibo?q=%E6%98%93%E6%AC%A1%E5%85%83&Refer=STopic_history"
           ]
for url in url_list:
    html = get_html(url)
    extract = extract_links.Extract(url, html, "易次元")
    url_list = extract.get_url_list()
    print(url_list)

# ['https://tieba.baidu.com/home/main?un=%E6%98%93%E6%AC%A1%E5%85%83&from=tieba']
# ['https://weibo.com/6509857538?refer_flag=1001030103_', 'https://app.weibo.com/t/feed/2nxWC7', 'https://k.sina.cn/article_5790946818_1592ad6020010112vs.html?from=animation&wm=3049_0032', 'https://c.m.163.com/news/a/EQ35KNJQ00318PFH.html?spss=newsapp']
```
