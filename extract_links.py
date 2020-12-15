from lxml import etree
from collections import Counter
from urllib.parse import unquote
import re


class Extract(object):
    __slots__ = ['url', 'html', 'keyword']

    def __init__(self, url, html, keyword):
        self.url = url
        self.html = html
        self.keyword = keyword

    def get_xpath_content(self):
        """
        页面匹配xpath
        :return: html对象
        """
        tree = etree.HTML(self.html)
        return tree

    # @typeassert(str)
    def get_url_font_website(self) -> tuple:
        """
        :判断是https还是http，还有网址，方便补齐链接
        """
        # https://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E6%98%93%E6%AC%A1%E5%85%83
        new_url = self.url[self.url.find('//') + 2:]
        end = new_url.find('/')
        website = new_url[:end]
        if 'https' in self.url:
            return 'https', website
        return 'http', website

    # @typeassert(str)
    @staticmethod
    def judge_u_and_num(url: str) -> bool:
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
    @staticmethod
    def judge_other_china_str(url: str, keyword: str) -> bool:
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
    def get_url(self) -> list:
        # 搜索title系列：//a[contains(@title, "易次元")]/@href
        """
        判断标准：
        1、首先找到全部关键字的a标签，a标签中的子标签要是有关键字的话就保存超链接
        2、第1步不满足直接找父标签，父标签中所有子标签值拼凑有关键字的话就保存超链接
        3、第2步要是不满足的话就直接找父的父标标签，要是父的标签中的子标签拼凑含有关键字的话就保存超链接
        """
        disable_tag = ["title", "head", "script"]
        # xpath('//*[contains(text(), $val)]', val=keyword)
        data = self.get_xpath_content().xpath('//*[contains(text(), $val)]', val=self.keyword)
        # xpath('//a[contains(@title, $val)]/@href', val=keyword)
        title_href = self.get_xpath_content().xpath('//a[contains(@title, $val)]/@href', val=self.keyword)
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
        judge_type, website = self.get_url_font_website()
        # 超链接补齐
        urls = ["//" + website + url if website[website.find('.') + 1:] not in url else url for url in urls]
        title_href = [judge_type + ':' + url if 'http' not in url else url for url in title_href]
        title_href = [url for url in title_href if '//' in url]
        new_urls = [judge_type + ':' + url if 'http' not in url else url for url in urls] + title_href
        new_urls = list(Counter([url for url in new_urls if url is not None]).keys())
        new_urls = [url for url in new_urls if self.judge_u_and_num(url)]
        new_urls = [url for url in new_urls if self.judge_other_china_str(url, self.keyword)]
        return new_urls
