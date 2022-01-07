# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json

class dekbedSpider(Spider):
    name = "hema_dekbedovertrekken"
    start_urls = ['https://www.hema.nl/wonen-slapen/slapen/dekbedovertrek']

    use_selenium = False
    count = 0
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse, meta={'page':1})
    def parse(self, response):
        products = response.xpath('//div[@class="product-container"]')
        for i, product_tag in enumerate(products):
            item = OrderedDict()
            item['name'] = product_tag.xpath('.//div[@class="product-info"]/h3/a/span/text()').extract_first()
            item['url'] = 'https://www.hema.nl' + product_tag.xpath('//div[@class="product-info"]/h3/a/@href').extract_first()
            item['price'] = product_tag.xpath('.//meta[@itemprop="price"]/@content').extract_first()

            attrs = product_tag.xpath('//ul[@class="bulleted"]/li')
            for li in attrs:
                key = li.xpath('./span[@class="label"]/text()').extract_first()
                val = li.xpath('./span[@class="value"]/text()').extract_first()
                if 'maat:' in key:
                    item['materiaal samenstelling'] = val.strip()
                elif 'kwaliteit bad' in key:
                    item['kwaliteit bad/bedtextiel'] = val.strip()
                elif 'soort instopstrook' in key:
                    item['soort instopstrook'] = val.strip()



            gratis_tags = product_tag.xpath('./following-sibling::div[@class="gratis-info"]//ul/li/text()').extract()
            item['delivery'] = gratis_tags[0]
            item['delivery_free'] = gratis_tags[1]
            yield item

        next_url = response.xpath('//a[@class="next"]/@href').extract_first()
        if next_url:
            yield Request(response.urljoin(next_url), self.parse)






