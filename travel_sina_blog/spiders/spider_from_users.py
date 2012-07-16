# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from scrapy.contrib.spiders import CrawlSpider
from redis import Redis
from scrapy.http.request import Request
from scrapy.selector import HtmlXPathSelector
import time
import random

cache = Redis()
user_blog_index = lambda s: 'http://blog.sina.com.cn/s/articlelist_%s_0_1.html' %s
user_blog_list = lambda i: "http://blog.sina.com.cn/s/articlelist_1274396622_0_%i.html" %i

class Spider(CrawlSpider):
  name = 'sina_users'
  allowed_domains = ['sina.com.cn']
  start_urls = ['http://travel.sina.com.cn', ]

  def parse(self, response):
    keys = cache.keys('SINA:*')
    for key in keys:
      uid = key[5:]
      request = Request(url=user_blog_index(uid), callback=self.parse_blog_pages)
      yield request

  def parse_blog_pages(self, response):
    hxs = HtmlXPathSelector(response)
    try:
      page_total = hxs.select('//ul[@class="SG_pages"]/span/text()')[0].extract()[1:-1]
    except Exception as err:
      print("Parse blog pages err %s" %err)
      return

    print("Referer url is %s" %response.request.url)
    print("Total page is %s" %page_total)
    for i in range(1, int(page_total)+1):
      url = user_blog_list(i)
      request = Request(url=url, callback=self.parse_blog_detail)
      yield request

  def parse_blog_detail(self, response):
    hxs = HtmlXPathSelector(response)
    urls = hxs.select('//div[@class="articleList"]/div/p/span[@class="atc_title"]/a/@href').extract()
    for url in urls:
      request = Request(url=url, callback=self.parse_blog)
      yield request

  def parse_blog(self, response):
    path = 'data/spider_%d/%s.html' %(int(random.random()*10), response.request.url[31:-5])
    data = response.body
    file = open(path, 'w')
    file.write(data)
    file.close()
    print("Parsed url %s" %response.request.url)
    time.sleep(1)