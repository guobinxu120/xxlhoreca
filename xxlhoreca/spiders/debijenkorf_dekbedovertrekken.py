# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json

class dekbedSpider(Spider):
    name = "debijenkorf_dekbedovertrek"
    start_urls = ['https://www.debijenkorf.nl/slaapkamer/dekbedovertrekken']

    use_selenium = False
    count = 0
    reload(sys)
    sys.setdefaultencoding('utf-8')


    def parse(self, response):
        products = response.xpath('//a[@itemprop="url"]/@href').extract()
        for i, url in enumerate(products):
            # url = product.xpath('./div/a/@href').extract_first()
            yield Request(response.urljoin(url), self.finalParse)
            # break
        next = response.xpath('//li[@class="dbk-pagination--next"]/a/@href').extract_first()
        if next:
            url = response.urljoin(next)
            yield Request(url, callback=self.parse)

    # def parse_option(self, response):
    #     option_tags = response.xpath('//select[@id="product-variants"]/option')
    #     for option_tag in option_tags:
    #         id = option_tag.xpath('./@value').extract_first()
    #         variant = option_tag.xpath('./text()').extract_first()
    #         disabled = option_tag.xpath('./@disabled')
    #         if not disabled:
    #             if id:
    #                 url = response.url+ '?id={}'.format(id)
    #                 yield Request(url, self.finalParse, meta={'variant':variant}, dont_filter=True)
    #             else:
    #                 yield Request(response.url, self.finalParse, meta={'variant':variant}, dont_filter=True)

    def finalParse(self, response):
        try:
            item = OrderedDict()
            item['Brand'] = response.xpath('//a[@data-role="BRAND"]/text()').extract_first()
            item['Name'] = response.xpath('//h1[@data-test="title"]/text()').extract_first()
            item['Url'] = response.url
            try:
                rating = response
                item['Rating'] = response.xpath('//span[@class="rating-stars__value"]/span/span/text()').extract_first()
            except:
                item['Rating'] = ''
            #
            item['Reviews'] = response.xpath('//a[@title="reviews"]/span/text()').extract_first()
            options = response.xpath('//div[@class="accordion__body"]//li/text()').extract()
            for option in options:
                if 'Materiaal:' in option:
                    item['Materiaal'] = option.split(':')[-1].strip()
                elif 'Instopstrook:' in option:
                    item['Instopstrook'] = option.split(':')[-1].strip()

            oldprices = response.xpath('//div[@data-dbk-product-summary]//span[contains(@class,"dbk-price_old")]/text()').re(r'[\d,.]+')
            oldprice = 0.0
            if oldprices:
                oldprice = float(oldprices[0].replace('.', '').replace(',', '.'))

            oldprices = response.xpath('//div[@data-dbk-product-summary]//span[contains(@class, "dbk-price_primary")]/text()').re(r'[\d,.]+')
            price = 0.0
            if oldprices:
                price = float(oldprices[0].replace('.', '').replace(',', '.'))

            item['Delivery'] = response.xpath('//button[@class="btn btn--link dbk-delivery-info d-block"]/text()').extract_first()

            options = json.loads(response.body.split('Data.product =')[-1].split('};')[0] + '}')
            if 'variantProducts' in options['product'].keys() and len(options['product']['variantProducts']) > 0:
                for variant in options['product']['variantProducts']:
                    item['maat_option'] = variant['size']
                    item['price'] = variant['sellingPrice']['value']
                    try:
                        item['old_price'] = variant['overriddenPrices'][0]['value']
                    except:
                        item['old_price'] = ''
                    item['levertijd'] = variant['leadTimeText']
                    yield item
            else:
                item['maat_option'] = ''
                item['price'] = price
                item['old_price'] = oldprice
                item['levertijd'] = ''
                yield item



        except Exception as e:
            print e.message

