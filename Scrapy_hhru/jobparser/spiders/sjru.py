import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://spb.superjob.ru/vacancy/search/?keywords=python',
                  'https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bt%5D%5B0%5D=4']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@rel = 'next']//@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//div[contains(@class, 'f-test-search-result-item')]//div/div[contains(@class, 'f-test-vacancy-item')]//div/span/a[contains(@target, '_blank')]/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        # name = response.xpath("//div[contains(@class, 'f-test-search-result-item')]//div/div[contains(@class, 'f-test-vacancy-item')]//div/span/a[contains(text(), '')]/text()").get()
        name = response.xpath("//div[contains(@class, 'f-test-search-result-item')]//div/div[contains(@class, 'f-test-vacancy-item')]//div/span/a[contains(@target, '_blank')]/text()").getall()
        salary = response.xpath("//div[contains(@class, 'f-test-vacancy-item')]//span[contains(@class,  'f-test-text-company-item-salary')]/span[contains(@class, '_2Wp8I')]/text()").getall()
        # salary = response.xpath("//div[contains(@class, 'f-test-vacancy-item')]//span[contains(@class,  'f-test-text-company-item-salary')]//text()").getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)


