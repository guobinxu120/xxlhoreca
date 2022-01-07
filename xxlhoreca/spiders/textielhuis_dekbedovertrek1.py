# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json, re

class dekbedSpider(Spider):
    name = "textielhuis_dekbedovertrek"
    start_urls = ['https://www.textielhuis.nl/beddengoed/dekbedovertrekken']

    use_selenium = True
    count = 0
    reload(sys)
    models = {}
    sys.setdefaultencoding('utf-8')
    headers = ['name', 'url', 'price', 'delivery']
    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse, meta={'page':1})
    def parse(self, response):
        products = response.xpath('//div[@class="product-thumb product-wrapper "]/div/a/@href').extract()

        for i, url in enumerate(products):
            yield Request(response.urljoin(url), self.finalParse, dont_filter=True)

        nexts = response.xpath('//li/a[text()=">"]/@href').extract_first()
        page = response.meta['page']
        if nexts:
            # url = nexts[-1].xpath('./a/@href').extract_first()
            # page += 1
            # url = 'https://www.smulderstextiel.nl/dekbedovertrek/?page={}'.format(page)
            yield Request(nexts, callback=self.parse, dont_filter=True, meta={'page':page})

    # def parse_option(self, response):
    #     options = response.xpath('//select[@class="select roundless skin-gray"]')
    #     if options:
    #         url = options[0].xpath('./option/@data-link').extract_first()
    #         yield Request(response.urljoin(url), self.finalParse, dont_filter=True)


    def finalParse(self, response):
        # try:
            item = OrderedDict()
            for key in self.headers:
                item[key] = None
            item['brand'] = response.xpath('//li[@class="p-brand"]/a/text()').extract_first()
            item['name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
            item['url'] = response.url

            item['delivery'] = ''.join(response.xpath('//div[@class="journal-custom-tab"]//table//tr[1]/td[1]/text()').extract()).strip()
            item['Materiaal'] = ''.join(response.xpath('//div[@id="tab-description"]/ul/li[2]/text()').extract()).strip()
            # item['delivery'] = ''.join(response.xpath('//dt[text()="Levertijd"]//following-sibling::dd/div/div//text()').extract()).strip()

            price_tag = response.xpath('//span[@class="price"]')
            oldprices = response.xpath('//li[@class="price-old"]/text()').re(r'[\d,.]+')
            oldprice = None
            if oldprices:
                oldprice = ''.join(oldprices).replace(' ', '').replace(',', '.')
                oldprice = float(oldprice)
                item['old_price'] = oldprice
            prices = response.xpath('//li[@class="price-new"]/text()').re(r'[\d,.]+')
            if len(prices) < 1:
                prices = response.xpath('//li[@class="product-price"]/text()').re(r'[\d,.]+')
            price = float(''.join(prices).replace(' ', '').replace(',', '.'))
            item['price'] = ''.join(prices).replace(' ', '').replace(',', '.')

            id = response.xpath('//input[@name="product_id"]/@value').extract_first()
            options = response.xpath('//label[contains(text(),"Maat")]/parent::div/select/option')
            maat= response.xpath('//label[contains(text(),"Maat")]/parent::div/select/option[2]/text()').extract_first()
            if maat:
                item['maat'] = maat.strip()
            key1 = response.xpath('//label[contains(text(),"Maat")]/parent::div/select/@name').extract_first()
            key2 = response.xpath('//label[contains(text(),"Kleur")]/parent::div/select/@name').extract_first()
            val2= response.xpath('//label[contains(text(),"Kleur")]/parent::div/ul/li/@data-value').extract_first()
            if len(options) == 2:
                yield item
            elif len(options) > 2:
                for i, li in enumerate(options):
                    if i == 0: continue
                    if i == 1:
                    # selected = li.xpath('./@class').extract_first()
                    # if selected and selected == "selected":
                        yield item
                        continue
                    else:
                        val1 = re.findall(r'[\d,.]+', li.xpath('./text()').extract_first().strip().split('   ')[-1])[0]
                        val = float(val1.replace(',', '.'))
                        if oldprice:
                            item['old_price'] = oldprice + val
                        item['price'] = price + val
                        item['maat'] = li.xpath('./text()').extract_first().replace('  ', '').strip()
                        yield item








