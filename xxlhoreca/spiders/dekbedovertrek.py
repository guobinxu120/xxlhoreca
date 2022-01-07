# -*- coding: utf-8 -*-
from scrapy import Spider, Request
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time

class dekbedSpider(Spider):
    name = "dekbedovertrek"
    start_urls = ['https://www.dekbed-discounter.nl/dekbedovertrek/']

    use_selenium = False
    count = 0
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def parse(self, response):
        category = response.xpath('//form[@id="formFilter"]//input[@name="filter[]"]/@value').extract()
        for cat in category:
            label = response.xpath('//label[@for="filter_{}"]/span/text()'.format(cat)).extract_first()
            url = 'https://www.dekbed-discounter.nl/dekbedovertrek/?sort=default&mode=grid&limit=24&max=100&filter[]={}&sort=default'.format(cat)
            # time.sleep(1)
            yield Request(url, self.parse_products, meta={'category': cat, 'label':label})

    def parse_products(self, response):
        products = response.xpath('//div[@class="row"]/div[contains(@class,"product-block")]')
        for i, product in enumerate(products):
            item = OrderedDict()
            item['Name'] = product.xpath('.//span[@class="product-title"]/text()').extract_first()
            item['Price'] = product.xpath('.//span[@class="product-price"]/text()').extract_first()
            if item['Price']:
                item['Price'] = item['Price'].replace('.', '').replace(',', '.')
            item['Price_Old'] = product.xpath('.//span[@class="product-price-old"]/text()').extract_first()
            if item['Price_Old']:
                item['Price_Old'] = item['Price_Old'].replace('.', '').replace(',', '.')
            item['Filter'] = response.meta['label']
            item['Url'] = product.xpath('./div/a/@href').extract_first()
            print self.count
            self.count += 1
            yield item

        next = response.xpath('//a[@class="next"]/@href').extract_first()
        if next:
            url = response.urljoin(next)
            cat = response.meta['category']
            url = url + '?filter%5B0%5D={}&limit=24?sort=default&mode=grid&limit=24&max=100&filter[]={}&sort=default'.format(cat, cat)
            yield Request(url, callback=self.parse_products, meta=response.meta)
