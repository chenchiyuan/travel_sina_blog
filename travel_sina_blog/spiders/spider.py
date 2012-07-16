# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider
from scrapy.http.request import Request
from scrapy.selector import HtmlXPathSelector

import time
import re
import redis
import random
DIRECTORS = 10

cache = redis.Redis()
cache_key = lambda s: '%s%s' %('SINA:', s)

blog_url = lambda s: '%s%s?tj=1' %('http://blog.sina.com.cn/s/', s)
user_blog_index = lambda s: 'http://blog.sina.com.cn/s/articlelist_%s_0_1.html' %s
user_blog_list = lambda i: "http://blog.sina.com.cn/s/articlelist_1274396622_0_%d.html" %i

pattern = "blog_[a-zA-Z0-9_]*\.html"

class Spider(CrawlSpider):
  name = 'sina'
  allowed_domains = ['travel.sina.com.cn', 'blog.sina.com.cn']
  start_urls = ['http://travel.sina.com.cn/109/blog/w/list.html',
    'http://travel.sina.com.cn/109/blog/chn/list.html']

  def parse(self, response):
    hxs = HtmlXPathSelector(response)
    arrays = hxs.select('//div[@id="info"]').extract()
    data = arrays[0]

    urls = re.findall(pattern=pattern, string=data)
    for url in urls:
      request = Request(url=blog_url(url), callback=self.parse_blog_url)
      yield request

  def parse_blog_url(self, response):
    hxs = HtmlXPathSelector(response)
    try:
      uid = hxs.select('//div[@id="blogads"]/@uid')[0].extract()
    except:
      uid = ''

    try:
      if not uid:
        uid = hxs.select('//div[@class="blognavInfo"]/span[@class="last"]/a/@href')[0].extract()
        uid = uid[34:-5]
    except Exception as err:
      print("Parse uid 2 err %s" %err)
      return

    key = cache_key(uid)
    if cache.exists(key):
      return

    cache.incr(name=key)
    url = user_blog_index(uid)
    request = Request(url=url, callback=self.parse_blog_pages)
    yield request

  def parse_blog_pages(self, response):
    hxs = HtmlXPathSelector(response)
    try:
      page_total = hxs.select('//ul[@class="SG_pages"]/span/text()')[0].extract()[1:-1]
    except Exception as err:
      print("Parse blog pages err %s" %err)
      return

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
    time.sleep(0.2)