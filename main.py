from lxml import etree
import asyncio
from pyppeteer import launch
from collections import Counter
import random
from urllib.parse import unquote
import time
import re
from retrying import retry
from typing import Any
from public import typeassert
import pysnooper


async def create_page(url_address: str, browser_obj):
    page = await browser_obj.newPage()
    # 是否启用JS，enabled设为False，则无渲染效果
    await page.setJavaScriptEnabled(enabled=True)
    await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,'
                                     '{ webdriver:{ get: () => false } }) }')
    await page.goto(url_address)
    return page


class Extract(object):
    __slots__ = ['browser', 'keyword']

    def __init__(self, browser, keyword):
        self.browser = browser
        self.keyword = keyword

    @staticmethod
    def get_xpath_content(html: str):
        """
        页面匹配xpath
        :param html: html页面
        :return: html对象
        """
        tree = etree.HTML(html)
        return tree

    @typeassert(str)
    def get_url_font_website(self, url: str) -> tuple:
        """
        :判断是https还是http，还有网址，方便补齐链接
        """
        # https://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E6%98%93%E6%AC%A1%E5%85%83
        new_url = url[url.find('//') + 2:]
        end = new_url.find('/')
        website = new_url[:end]
        if 'https' in url:
            return 'https', website
        return 'http', website

    # @typeassert(str)
    def judge_u_and_num(self, url: str) -> bool:
        # 判断第一种情况
        try:
            rule = re.search(r"/u/+\d+", url).group()
            num = rule[rule.find('/u/') + 3:]
            if len(num) >= 6:
                return False
            else:
                return True
        except AttributeError:
            return True

    # @typeassert(str, str)
    def judge_other_china_str(self, url: str, keyword: str) -> bool:
        # 判断第二种情况
        eachvalue = unquote(url, encoding='utf8')
        try:
            china_str = re.search('[\u4e00-\u9fa5]+[\u4e00-\u9fa5]', eachvalue).group()
            if keyword == china_str:
                return True
            else:
                return False
        except AttributeError:
            return True

    # @typeassert(list, str)
    def remove_useless_links(self, links: list, keyword: str) -> list:
        """
        去除无用链接，考虑情况如下：
        1、剔除链接特征中有u和一连串数字（数字长度大于6）例如 /u/4661165
        2、剔除链接含有包括关键词以外的中文关键字
        """
        new_links = [url for url in links if self.judge_u_and_num(url)]
        new_links = [url for url in new_links if self.judge_other_china_str(url, keyword)]
        return new_links

    # @typeassert(str, str, str)
    def get_url(self, start_url: str, html: str, keyword: str) -> list:
        # 搜索title系列：//a[contains(@title, "易次元")]/@href
        """
        判断标准：
        1、首先找到全部关键字的a标签，a标签中的子标签要是有关键字的话就保存超链接
        2、第1步不满足直接找父标签，父标签中所有子标签值拼凑有关键字的话就保存超链接
        3、第2步要是不满足的话就直接找父的父标标签，要是父的标签中的子标签拼凑含有关键字的话就保存超链接
        """
        disable_tag = ["title", "head", "script"]
        # xpath('//*[contains(text(), $val)]', val=keyword)
        data = self.get_xpath_content(html).xpath('//*[contains(text(), $val)]', val=keyword)
        # xpath('//a[contains(@title, $val)]/@href', val=keyword)
        title_href = self.get_xpath_content(html).xpath('//a[contains(@title, $val)]/@href', val=keyword)
        data = [item for item in data if item.tag not in disable_tag]
        urls = []
        for item_data in data:
            url = item_data.xpath('@href')
            if url:
                urls.extend(url)
            else:
                item_data_pre = item_data.getparent()
                try:
                    item_data_pre_url = item_data_pre.xpath(".//a/href")
                    item_data_pre.xpath("string(.)")
                    if item_data_pre_url:
                        item_data_pre_pre = item_data_pre.getparent().xpath('.//a/href')
                        urls.extend(item_data_pre_pre)
                    else:
                        try:
                            # 查找其中的a标签元素
                            element_link = item_data_pre.getparent().findall(".//a")[0]
                            link = element_link.xpath("@href")
                            urls.extend(link)
                        except IndexError:
                            # 没有超链接
                            pass
                except AttributeError:
                    # 匹配不到超链接
                    pass

        # 列表去重
        urls = list(Counter(urls).keys())
        judge_type, website = self.get_url_font_website(start_url)
        # 超链接补齐
        urls = ["//" + website + url if website[website.find('.') + 1:] not in url else url for url in urls]
        title_href = [judge_type + ':' + url if 'http' not in url else url for url in title_href]
        title_href = [url for url in title_href if '//' in url]
        new_urls = [judge_type + ':' + url if 'http' not in url else url for url in urls] + title_href
        new_urls = list(Counter([url for url in new_urls if url is not None]).keys())
        new_urls = [url for url in new_urls if self.judge_u_and_num(url)]
        new_urls = [url for url in new_urls if self.judge_other_china_str(url, keyword)]
        return new_urls

    async def get_data(self, url_address: str, page, keyword: str, address_name: dict) -> list:
        """
        获取url链接数据并写入日志
        :param keyword: 搜索关键字
        :param page: 网址页面
        :param url_address:url链接
        :param address_name:地址名称dict
        :return:url链接列表
        """
        while True:
            await page.reload()
            html = await page.content()
            url_list = self.get_url(url_address, html, keyword)
            try:
                url_list.remove(url_address)
            except ValueError:
                pass
            print(url_list)
            print(len(url_list))
            url_list_value = address_name[url_address]
            new_value = [url for url in url_list if url not in url_list_value]
            if new_value:
                # log.logger.warning(f"网址：{url_address}监控到新添加链接为:{new_value}")
                address_name[url_address] = url_list
                # return new_value
            else:
                pass
                # return None
                # pass
                # log.logger.warning(f"网址：{url_address}监控到无新链接添加")

            # log.logger.warning(f"网址：{url_address}包含的关键字链接列表为:{url_list}")


class Start(object):
    __slots__ = ['retry_num']

    def __init__(self, retry_num: int = 3):
        self.retry_num = retry_num

    def __str__(self):
        print("------start to extract links-------")

    # @typeassert(str, Any)
    async def main(self, keyword: str, *args):
        print("test", args)
        # proxy_list, address_list, address_name = kwargs[0], kwargs[1], kwargs[2]
        address_list, address_name = args[0]["address_list"], args[1]
        # proxy = 'http://' + random.choice(proxy_list)
        # print(f"使用代理：{proxy}发送请求")
        browser = await launch({
            'headless': False,  # 关闭无头模式
            # 'userDataDir': r'./temp',
            'args': [
                # '--proxy-server={}'.format(proxy),
                '--disable-extensions',
                '--hide-scrollbars',
                '--disable-bundled-ppapi-flash',
                '--mute-audio',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-gpu',
            ],
            'dumpio': True,
        })
        extract = Extract(browser, keyword)
        page_dict = {
            address: await create_page(address, browser) for address in address_list
        }
        print(page_dict)
        await asyncio.gather(
            *[extract.get_data(address, page, keyword, address_name) for address, page in page_dict.items()]
        )

    def get_retry_num(self):
        return self.retry_num

    # @retry(stop_max_attempt_number=get_retry_num)
    @pysnooper.snoop()
    def run(self, keyword, *args):
        address_list = args[0]
        address_name = {
          name: "" for name in address_list["address_list"]
        }
        asyncio.get_event_loop().run_until_complete(self.main(keyword, address_list, address_name))





