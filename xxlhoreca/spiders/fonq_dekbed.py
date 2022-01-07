# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json

class dekbedSpider(Spider):
    name = "fonq_dekbed"
    start_urls = ['https://www.fonq.nl/producten/categorie-dekbed/voorraad-ja/']

    use_selenium = True
    count = 0
    reload(sys)
    models = {}
    sys.setdefaultencoding('utf-8')
    headers = ['name', 'brand', 'url', 'price', 'old_price', 'rating', 'reviews', 'delivery', '6 uitvoeringen:', 'Maat',
               'Lengte', 'Breedte', 'Soort dekbed']
    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse, meta={'page':1})
    def parse(self, response):
        products = response.xpath('//div[@class="col-sm-4 col-xxs-6 "]//div[@class="product-body"]/a/@href').extract()

        for i, url in enumerate(products):
            yield Request(response.urljoin(url), self.parse_option, dont_filter=True)

        nexts = response.xpath('//nav[contains(@class,"pagination")]/ul/li')
        nav = nexts[-1].xpath('./@class').extract_first()
        if nav == "nav":
            url = nexts[-1].xpath('./a/@href').extract_first()
            yield Request(response.urljoin(url), callback=self.parse)


    def parse_option(self, response):
        options = response.xpath('//select[@class="select roundless skin-gray"]')
        if options:
            url = options[0].xpath('./option/@data-link').extract_first()
            yield Request(response.urljoin(url), self.finalParse, dont_filter=True)


    def finalParse(self, response):
        try:
            item = OrderedDict()
            for key in self.headers:
                item[key] = None
            item['brand'] = response.xpath('//div[@class="page-header__part page-header__brand"]/a/text()').extract_first()
            item['name'] = response.xpath('//div[@class="page-header"]/h1/text()').extract_first()
            item['url'] = response.url
            attr_data = json.loads(response.body.split('application/ld+json">')[-1].split('</script>')[0].strip())
            try:
                rating = attr_data['aggregateRating']['ratingValue']
                item['rating'] = rating.replace(',', '.')
                item['reviews'] = attr_data['aggregateRating']['reviewCount']
            except:
                pass

            item['price'] = attr_data['offers']['price']

            oldprices = response.xpath('//span[@class="c-price__original-value has-strike"]/text()').re(r'[\d,.]+')
            oldprice = 0.0
            if oldprices:
                oldprice = float(oldprices[0].replace('.', '').replace(',', '.'))
            item['old_price'] = oldprice
            item['delivery'] = response.xpath('//span[@class="delivery-description text text-uppercase"]/text()').extract_first().strip()


            options = response.xpath('//select[@class="select roundless skin-gray"]')
            next_url = None
            for i, select in enumerate(options):
                label = select.xpath('./parent::div/label/text()').extract_first().strip()
                val = select.xpath('./option[@selected="selected"]/text()').extract_first()
                item[label] = val
                next_tag = select.xpath('./option[@selected="selected"]/following-sibling::option[1]/@data-link').extract_first()
                if next_tag:
                    next_url = next_tag


            trs = response.xpath('//div[@class="col-sm-6"]/table//tr')
            for tr in trs:
                key = ''.join(tr.xpath('./td[1]//text()').extract()).strip()
                val = ''.join(tr.xpath('./td[2]//text()').extract()).strip()
                item[key] = val
                if not key in self.headers:
                    self.headers.append(key)

            yield item
            self.count += 1
            print(self.count)
            self.models[item['url']] = item

            if next_url:
                yield Request(response.urljoin(next_url), self.finalParse, dont_filter=True)

        except Exception as e:
            print(e.message)

            # yield item





