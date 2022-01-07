# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json

class dekbedSpider(Spider):
    name = "dekbed"
    start_urls = ['https://www.dekbed-discounter.nl/dekbed/']

    use_selenium = False
    count = 0
    reload(sys)
    sys.setdefaultencoding('utf-8')


    def parse(self, response):
        products = response.xpath('//div[@id="products-container"]/div[@class="row"]/div[contains(@class,"product-block")]')
        for i, product in enumerate(products):
            url = product.xpath('./div/a/@href').extract_first()
            yield Request(url, self.parse_option)
            # break
        next = response.xpath('//a[@class="next"]/@href').extract_first()
        if next:
            url = response.urljoin(next)
            yield Request(url, callback=self.parse)

    def parse_option(self, response):
        option_tags = response.xpath('//select[@id="product-variants"]/option')
        for option_tag in option_tags:
            id = option_tag.xpath('./@value').extract_first()
            variant = option_tag.xpath('./text()').extract_first()
            disabled = option_tag.xpath('./@disabled')
            if not disabled:
                if id:
                    url = response.url+ '?id={}'.format(id)
                    yield Request(url, self.finalParse, meta={'variant':variant}, dont_filter=True)
                else:
                    yield Request(response.url, self.finalParse, meta={'variant':variant}, dont_filter=True)

    def finalParse(self, response):
        item = OrderedDict()
        item['Name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
        item['Url'] = response.url
        try:
            rating = response.body.split('ratingValue')[-1].split(',')[0].replace('"', '')
            item['Rating'] = rating
        except:
            item['Rating'] = ''

        item['Reviews'] = response.xpath('//div[@class="yotpo-bottomline pull-left  star-clickable"]/a/text()').extract_first()

        item['Merk'] = response.xpath('//span[@itemprop="brand"]/text()').extract_first()
        item['Levertijd'] = ''.join(response.xpath('//span[@class="on-stock"]/text()').extract()).strip()
        item['Maat'] = response.meta['variant'].strip()
        item['Price'] = response.xpath('//span[@itemprop="price"]/text()').extract_first()
        if item['Price']:
            item['Price'] = item['Price'].replace('.', '').replace(',', '.')
        item['Price_Old'] = ''.join(response.xpath('//span[@class="price-old"]//text()').extract()).replace('.', '').replace(',', '.')

        specs = response.xpath('//div[@id="product-text"]/table//tr')
        for tr in specs:
            key = ''.join(tr.xpath('./td[1]//text()').extract()).strip()
            val = '\n'.join(tr.xpath('./td[2]//text()').extract()).strip().replace('&nbsp;', ' ')
            item[key] = val

        print(self.count)
        self.count += 1
        url = 'https://staticw2.yotpo.com/batch'
        id = response.xpath('//div[@class="yotpo bottomLine"]/@data-product-id').extract_first()
        app_key = response.body.split('src="//staticw2.yotpo.com/')[-1].split('/')[0]
        method = '%5B%7B%22method%22%3A%22main_widget%22%2C%22params%22%3A%7B%22pid%22%3A%22{}%22%7D%7D%2C%7B%22method%22%3A%22bottomline%22%2C%22params%22%3A%7B%22pid%22%3A%22{}%22%2C%22link%22%3Anull%2C%22skip_average_score%22%3Afalse%2C%22main_widget_pid%22%3A%22{}%22%7D%7D%5D'.format(id, id, id)
        formdata = {
            'methods': method,
            'app_key': app_key,
            'is_mobile': 'false',
            'widget_version': '2018-07-11_08-23-59'
        }
        headers= {
            'Accept': 'application/json'
        }
        ddd = [{"method":"main_widget","params":{"pid":id}},{"method":"bottomline","params":{"pid":id,"link":'null',"skip_average_score":'false',"main_widget_pid":id}}]
        formdata['methods'] = json.dumps(ddd)
        yield FormRequest(url, self.getReview, formdata=formdata, meta={'item':item}, headers=headers, dont_filter=True)

    def getReview(self, response):
        item = response.meta['item']
        try:
            jsondata = json.loads(response.body)
            Reviews = jsondata[0]['result'].split('Beoordelingen')[0].split('>')[-1]
            item['Reviews'] = Reviews
            yield item
        except:
            yield item


