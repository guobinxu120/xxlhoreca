# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json

class dekbedSpider(Spider):
    name = "beddengoed"
    start_urls = ['https://www.beddengoed.com/volwassenen/boxspring']

    use_selenium = False
    count = 0
    reload(sys)
    sys.setdefaultencoding('utf-8')


    def parse(self, response):
        products = response.xpath('//li[@class="item"]/div[1]/a/@href').extract()
        for i, url in enumerate(products):
            # url = product.xpath('./div/a/@href').extract_first()
            yield Request(url, self.finalParse)
            # break
        # next = response.xpath('//a[@class="next"]/@href').extract_first()
        # if next:
        #     url = response.urljoin(next)
        #     yield Request(url, callback=self.parse)

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
        item = OrderedDict()
        item['Name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
        item['Url'] = response.url
        # try:
        #     rating = response.body.split('ratingValue')[-1].split(',')[0].replace('"', '')
        #     item['Rating'] = rating
        # except:
        item['Rating'] = ''

        item['Reviews'] = response.xpath('//a[@id="goto-reviews-form"]/text()').extract_first()
        options = response.xpath('//div[@itemprop="description"]/text()').extract()
        for option in options:
            if 'Geschikt voor personen tot' in option:
                item['Geschikt'] = option.strip()
        oldprices = response.xpath('//span[contains(@id,"old-price")]/text()').re(r'[\d,.]+')
        oldprice = 0.0
        if oldprices:
            oldprice = float(oldprices[0].replace('.', '').replace(',', '.'))

        oldprices = response.xpath('//span[contains(@id,"product-price")]/text()').re(r'[\d,.]+')
        price = 0.0
        if oldprices:
            price = float(oldprices[0].replace('.', '').replace(',', '.'))

        matt_options = ['140 x 200 cm', '160 x 200 cm', '180 x 200 cm']
        maat = {}
        for i, option in enumerate(matt_options):
            if i ==0 :continue
            key = option
            val = 0
            maat[key] = float(val)

        Levering_options = response.xpath('//select[@class=" required-entry product-custom-option"]/option')
        Levering  = {}
        for i, option in enumerate(Levering_options):
            if i ==0 :continue
            key = option.xpath('./text()').extract_first()
            val = option.xpath('./@price').extract_first()
            Levering[key] = float(val)

        for key1 in maat.keys():
            for key2 in Levering.keys():
                item['maat'] = key1
                item['Levering'] = key2
                item['old_price'] = oldprice + maat[key1] + Levering[key2]
                item['price'] = price + maat[key1] + Levering[key2]
                item['Levertijd'] = '2/3 weken'
                item['verzending'] = 'GRATIS verzending!'
                yield item




