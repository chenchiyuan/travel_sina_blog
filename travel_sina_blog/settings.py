# Scrapy settings for travel_sina_blog project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
LOG_ENABLED = False
BOT_NAME = 'travel_sina_blog'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['travel_sina_blog.spiders']
NEWSPIDER_MODULE = 'travel_sina_blog.spiders'
DEFAULT_ITEM_CLASS = 'travel_sina_blog.items.TravelSinaBlogItem'
USER_AGENT = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.25 (KHTML, like Gecko) Chrome/12.0.706.0 Safari/534.25'
