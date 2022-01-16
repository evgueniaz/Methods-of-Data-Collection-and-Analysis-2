# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancies2712


    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['min_salary'], item['max_salary'], item['salary_currency'], item['salary_type'] = self.process_salary_hh(item['salary'])
        else:
            item['min_salary'], item['max_salary'], item['salary_currency'], item['salary_type'] = self.process_salary_sj(item['salary'])
        # del item['salary']
        # print()
        collection = self.mongobase[spider.name]
        if not collection.find_one(item):
            collection.insert_one(item)
        return item

    def process_salary_hh(self, salary):

        if salary[0] == 'от ' and salary[2] == ' до ':
            min_salary = int(salary[1].replace('\xa0', ''))
            max_salary = int(salary[3].replace('\xa0', ''))
            salary_type = salary[-1]
            salary_currency = salary[-2]
        elif salary[0] == 'до ':
            max_salary = int(salary[1].replace('\xa0', ''))
            salary_type = salary[4]
            salary_currency = salary[3]
        elif salary[0] == 'от ':
            min_salary = int(salary[1].replace('\xa0', ''))
            max_salary = None
            salary_type = salary[4]
            salary_currency = salary[3]
        else:
            min_salary = None
            max_salary = None
            salary_currency = ''
            salary_type = salary[0]
        return min_salary, max_salary, salary_currency, salary_type

    def process_salary_sj(self, salary):
        if salary[0] == 'По договорённости':
            salary_type = salary[0]
            min_salary = None
            max_salary = None
            salary_currency = ''
        elif salary[0] == 'до':
            max_salary = int(salary[1].replace('\xa0', ''))
            min_salary = None
            salary_currency = salary[2][0:3]
        elif salary[0] == 'от':
            min_salary = int(salary[1].replace('\xa0', ''))
            max_salary = None
            salary_currency = salary[2][0:3]
        else:
            min_salary = int(salary[0].replace('\xa0', ''))
            max_salary = int(salary[2].replace('\xa0', ''))
            salary_currency = salary[3][0:3]

        return min_salary, max_salary, salary_currency, salary_type