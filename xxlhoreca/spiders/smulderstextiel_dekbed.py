# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json

class dekbedSpider(Spider):
    name = "smulderstextiel_dekbed"
    start_urls = ['https://www.smulderstextiel.nl/dekbed-hoofdkussen/dekbed/']

    use_selenium = True
    count = 0
    reload(sys)
    models = {}
    sys.setdefaultencoding('utf-8')
    headers = ['name', 'url', 'price', 'delivery']
    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse, meta={'page':1})
    def parse(self, response):
        products = response.xpath('//div[contains(@class,"featureditem")]/a/@href').extract()

        for i, url in enumerate(products):
            yield Request(response.urljoin(url), self.finalParse, dont_filter=True)

        nexts = response.xpath('//a[@class="paging-next"]/@href').extract_first()
        page = response.meta['page']
        if page< 5:
            # url = nexts[-1].xpath('./a/@href').extract_first()
            page += 1
            url = 'https://www.smulderstextiel.nl/dekbedovertrek/?page={}'.format(page)
            yield Request(url, callback=self.parse, dont_filter=True, meta={'page':page})

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
            item['brand'] = response.xpath('//a[@itemprop="brand"]/text()').extract_first()
            item['name'] = response.xpath('//span[@itemprop="name"]/text()').extract_first()
            item['url'] = response.url

            item['Tijk'] = ''.join(response.xpath('//dt[text()="Tijk"]//following-sibling::dd/div/div//text()').extract()).strip()
            item['Vulling'] = ''.join(response.xpath('//dt[text()="Vulling"]//following-sibling::dd/div/div//text()').extract()).strip()
            item['Vulgewicht'] = ''.join(response.xpath('//dt[text()="Vulgewicht"]//following-sibling::dd/div/div//text()').extract()).strip()
            item['Warmteklasse'] = ''.join(response.xpath('//dt[text()="Warmteklasse"]//following-sibling::dd/div/div//text()').extract()).strip()
            item['delivery'] = ''.join(response.xpath('//dt[text()="Levertijd"]//following-sibling::dd/div/div//text()').extract()).strip()

            price_tag = response.xpath('//span[@class="price"]')
            oldprices = response.xpath('//span[@class="price"]//div[@class="ofprice"]/text()').re(r'[\d,.]+')
            oldprice = None
            if oldprices:
                oldprice = ''.join(oldprices).replace(' ', '').replace(',', '.')
            item['old_price'] = oldprice
            prices = response.xpath('//span[@class="price"]//strong/text()').re(r'[\d,.]+')
            item['price'] = ''.join(prices).replace(' ', '').replace(',', '.')

            id = response.url.split('/shopart')[0].split('-')[-1]
            options = response.xpath('//select[@name="property5"]/option')
            next_url = None
            flag = False
            for i, select in enumerate(options):
                option_id = select.xpath('./@value').extract_first()
                txt_option = select.xpath('./text()').extract_first()
                selected = select.xpath('./@selected').extract_first()
                if not selected:
                    item['maat'] = txt_option
                    option_rul = 'https://www.smulderstextiel.nl/webshop/action/showdetail/shopid/{}/ajax/1/lastSel/5/property5/{}/'.format(id, option_id)
                    yield Request(option_rul, self.finalOption, meta={'item':item})
                    # flag = True
                else :
                    item['maat'] = txt_option
                    yield item

    def finalOption(self, response):
        item = response.meta['item']
        # item['url'] = response.url
        item['Tijk'] = ''.join(response.xpath('//dt[text()="Tijk"]//following-sibling::dd/div/div//text()').extract()).strip()
        item['Vulling'] = ''.join(response.xpath('//dt[text()="Vulling"]//following-sibling::dd/div/div//text()').extract()).strip()
        item['Vulgewicht'] = ''.join(response.xpath('//dt[text()="Vulgewicht"]//following-sibling::dd/div/div//text()').extract()).strip()
        item['Warmteklasse'] = ''.join(response.xpath('//dt[text()="Warmteklasse"]//following-sibling::dd/div/div//text()').extract()).strip()
        item['delivery'] = ''.join(response.xpath('//dt[text()="Levertijd"]//following-sibling::dd/div/div//text()').extract()).strip()

        price_tag = response.xpath('//span[@class="price"]')
        oldprices = response.xpath('//span[@class="price"]//div[@class="ofprice"]/text()').re(r'[\d,.]+')
        oldprice = None
        if oldprices:
            oldprice = ''.join(oldprices).replace(' ', '').replace(',', '.')
        item['old_price'] = oldprice
        prices = response.xpath('//span[@class="price"]//strong/text()').re(r'[\d,.]+')
        item['price'] = ''.join(prices).replace(' ', '').replace(',', '.')
        yield item
            # yield item





