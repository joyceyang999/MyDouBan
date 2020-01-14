# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item,Field

class MydoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
class UserFollow(Item):
    user_id = Field()
    user_follow_id = Field()

class User(Item):
    id = Field()
    head_thumb = Field()
    douban_id = Field()
    douban_user_url = Field()
    nickname = Field()
    created_at = Field()




