import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from sekse.items import Article


class SekseSpider(scrapy.Spider):
    name = 'sekse'
    start_urls = ['https://www.sek.se/nyheter-och-pressmeddelanden/']

    def parse(self, response):
        links = response.xpath('//h3/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//ul[@class="c-pager__list"]/li[last()]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = " ".join(response.xpath('//div[@class="o-row -small c-label"]/text()').get().split()[1:])
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="o-8-of-12@xlarge u-left@xlarge"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
