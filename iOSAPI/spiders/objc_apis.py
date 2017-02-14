# -*- coding: utf-8 -*-

import scrapy

from iOSAPI.data_db.sqlite_handler import IOSAPIdb

class ApiSpider(scrapy.Spider):
	name = "objcApi"
	allowed_domains = ["developer.apple.com"]
	start_urls = [
		"https://developer.apple.com/reference"
	]

	#api tag定义
	api_tag = {"cldata": "类数据", "clm": "类方法", "instm": "实例方法", "instp": "实例属性"}

	def __init__(self):
		print("init call...")

		self.db = IOSAPIdb()
		self.db.init_tables()

		#html中元素标签名
		#./reference页标签名
		self.xpath_category_row = 'div[@class="category row"]'
		self.xpath_category_details = 'div[@class="category-details column large-3 medium-3 small-12"]'
		self.xpath_category_title = 'h2[@class="category-title"]'
		self.xpath_category_col = 'div[@class="column large-9 medium-9 small-12"]'
		self.xpath_category_list = 'ul[@class="category-list"]'
		self.xpath_category_list_item = 'li[@class="category-list-item"]'

		#./reference/(framework)标签名
		self.xpath_framework_symbols = 'div[@class="task-symbols"]'
		self.xpath_framework_symbols_item = 'div[@class="symbol cl"]'

		#./reference/(framework)/(class)标签名
		self.xpath_class_symbols = 'div[@class="task-symbols"]'
		self.xpath_class_symbols_cldata = 'div[@class="symbol cldata"]'
		self.xpath_class_symbols_clm = 'div[@class="symbol clm"]'
		self.xpath_class_symbols_clp = 'div[@class="symbol clp"]'
		self.xpath_class_symbols_instm = 'div[@class="symbol instm"]'
		self.xpath_class_symbols_instp = 'div[@class="symbol instp"]'

		#./reference/(framework)/(class)/(api)标签名
		self.xpath_sdk = 'li[@class="topic-summary-section-item sdk"]'

	def parse(self, response):
		print("start call parse...")

		#category xpath路径
		xpath_category = '//{}/{}/{}/text()'.format(self.xpath_category_row, self.xpath_category_details, self.xpath_category_title)
		print("xpath_category: {}".format(xpath_category))
		category_names = response.xpath(xpath_category).extract()
		print("category_names are : %s" % category_names)

		for category_name in category_names:
			# sql = "INSERT INTO category(name) VALUES(?)"
			# db.insert_data(sql, (category_name,))  #插入数据到category

			xpath_category_id = category_name.lower().replace(" ", "-")
			#frameworks-names xpath路径
			xpath_framework_names = '//div[@id="{}"]/{}/{}/{}/a/text()'.format(xpath_category_id, self.xpath_category_col, \
				self.xpath_category_list, self.xpath_category_list_item)
			print("xpath_framework_names: {}".format(xpath_framework_names))

			#frameworks-urls xpath路径
			xpath_framework_urls = '//div[@id="{}"]/{}/{}/{}/a/@href'.format(xpath_category_id, self.xpath_category_col, \
				self.xpath_category_list, self.xpath_category_list_item)
			print("xpath_framework_urls: {}".format(xpath_framework_urls))

			#得到framework_names list
			framework_names = response.xpath(xpath_framework_names).extract()
			print("framework_names: {}".format(framework_names))
			#得到framework_urls list
			framework_urls = response.xpath(xpath_framework_urls).extract()
			print("framework_urls: {}".format(framework_urls))

			# sql = "SELECT id FROM category WHERE name='{}'".format(category_name) 
			# category_id = db.fetch_data(sql) #获取framework外键category_id
			# print("category_id: {}".format(category_id))

			sql = "INSERT INTO framework(name, url, category) VALUES(?,?,?)"
			for index in range(len(framework_names)):
				self.db.insert_data(sql, (framework_names[index], framework_urls[index], category_name)) #插入framework表

				#发一个具体的framework url请求
				framework_url = "https://{}{}?language=objc".format(ApiSpider.allowed_domains[0], framework_urls[index])
				yield scrapy.Request(framework_url, callback=self.parse_framework_content)

	def parse_framework_content(self, response):
		print("start call parse_framework_content...")

		db_framework_url = response.url.split("https://{}".format(ApiSpider.allowed_domains[0]))[1].split("?")[0]
		print("parse_framework_content db_framework_url: {}".format(db_framework_url))

		#获取class外键framework_id
		framework_id = self.get_db_foreign_key("framework", db_framework_url)
		print("class 外键 framework_id: {}".format(framework_id))

		#获取 类 相关信息
		class_names, class_urls = self.get_info_with_symbols(response, self.xpath_framework_symbols, self.xpath_framework_symbols_item)
		print("class_names: {}".format(class_names))
		print("class_urls: {}".format(class_urls))

		sql = "INSERT INTO class(name, url, framework_id) VALUES(?,?,?)"
		for index in range(len(class_names)):
			self.db.insert_data(sql, (class_names[index], class_urls[index], framework_id[0]))  #插入class表

			#发一个具体的class url请求
			class_url = "https://{}{}".format(ApiSpider.allowed_domains[0], class_urls[index])
			print("yield scrapy request: {}".format(class_url))
			yield scrapy.Request(class_url, callback=self.parse_class_content)

	def parse_class_content(self, response):
		print("start call parse_class_content...")

		db_class_url = response.url.split("https://{}".format(ApiSpider.allowed_domains[0]))[1]
		print("parse_class_content db_class_url: {}".format(db_class_url))

		#获取objcApi外键class_id
		class_id = self.get_db_foreign_key("class", db_class_url)
		print("objcApi 外键 class_id: {}".format(class_id))

		sql = "INSERT INTO objcApi(name, sdk, url, tag, class_id) VALUES(?,?,?,?,?)"

		#获取 类数据 相关信息
		cldata_names, cldata_urls = self.get_info_with_symbols(response, self.xpath_class_symbols, self.xpath_class_symbols_cldata)
		print("clm_names: {}".format(cldata_names))
		print("clm_urls: {}".format(cldata_urls))
		for index in range(len(cldata_names)):  #插入objcApi表
			self.db.insert_data(sql, (cldata_names[index].strip(), "", cldata_urls[index], ApiSpider.api_tag["cldata"], class_id[0]))

			#发一个具体的类数据请求
			cldata_url = "https://{}{}".format(ApiSpider.allowed_domains[0], cldata_urls[index])
			print("yield scrapy request: {}".format(cldata_url))
			yield scrapy.Request(cldata_url, callback=self.parse_api_content)

		#获取 类方法 相关信息
		clm_names, clm_urls = self.get_info_with_symbols(response, self.xpath_class_symbols, self.xpath_class_symbols_clm)
		print("clm_names: {}".format(clm_names))
		print("clm_urls: {}".format(clm_urls))
		for index in range(len(clm_names)):  #插入objcApi表
			self.db.insert_data(sql, (clm_names[index].strip(), "", clm_urls[index], ApiSpider.api_tag["clm"], class_id[0]))

			#发一个具体的类方法请求
			clm_url = "https://{}{}".format(ApiSpider.allowed_domains[0], clm_urls[index])
			print("yield scrapy request: {}".format(clm_url))
			yield scrapy.Request(clm_url, callback=self.parse_api_content)

		#获取 实例方法 相关信息
		instm_names, instm_urls = self.get_info_with_symbols(response, self.xpath_class_symbols, self.xpath_class_symbols_instm)
		print("instm_names: {}".format(instm_names))
		print("instm_urls: {}".format(instm_urls))
		for index in range(len(instm_names)):  #插入objcApi表
			self.db.insert_data(sql, (instm_names[index].strip(), "", instm_urls[index], ApiSpider.api_tag["instm"], class_id[0]))

			#发一个具体的实例方法请求
			instm_url = "https://{}{}".format(ApiSpider.allowed_domains[0], instm_urls[index])
			print("yield scrapy request: {}".format(instm_url))
			yield scrapy.Request(instm_url, callback=self.parse_api_content)

		#获取 实例属性 相关信息
		instp_names, instp_urls = self.get_info_with_symbols(response, self.xpath_class_symbols, self.xpath_class_symbols_instp)
		print("instp_names: {}".format(instp_names))
		print("instp_urls: {}".format(instp_urls))
		for index in range(len(instp_names)):  #插入objcApi表
			self.db.insert_data(sql, (instp_names[index].strip(), "", instp_urls[index], ApiSpider.api_tag["instp"], class_id[0]))

			#发一个具体的实例属性请求
			instp_url = "https://{}{}".format(ApiSpider.allowed_domains[0], instp_urls[index])
			print("yield scrapy request: {}".format(instp_url))
			yield scrapy.Request(instp_url, callback=self.parse_api_content)

	def parse_api_content(self, response):
		print("start call parse_api_content...")

		db_api_url = response.url.split("https://{}".format(ApiSpider.allowed_domains[0]))[1]
		print("parse_api_content db_api_url: {}".format(db_api_url))

		#api sdks xpath路径
		xpath_sdk_names = '//{}/span/text()'.format(self.xpath_sdk)
		print("xpath_sdk_names: {}".format(xpath_sdk_names))
		sdk_names = response.xpath(xpath_sdk_names).extract()
		print("sdk_names are : {}".format(sdk_names))

		db_sdk = ""
		for sdk_name in sdk_names:
			if "iOS" in sdk_name:
				db_sdk = sdk_name
				break

		sql = '''UPDATE objcApi SET sdk = ? WHERE url = ?'''
		self.db.update_data(sql, (db_sdk, db_api_url))

	def get_info_with_symbols(self, response, xpath_class_symbols, xpath_class_symbols_item):
		'''''获取 类或者api 相关信息'''
		print("start call get_info_with_symbols")
		#info names xpath路径
		xpath_info_names = '//{}/{}/a/code/text()'.format(xpath_class_symbols, xpath_class_symbols_item)
		print("xpath_info_names: {}".format(xpath_info_names))
		info_names = response.xpath(xpath_info_names).extract()

		#info urls xpath路径
		xpath_info_urls = '//{}/{}/a/@href'.format(xpath_class_symbols, xpath_class_symbols_item)
		print("xpath_info_urls: {}".format(xpath_info_urls))
		info_urls = response.xpath(xpath_info_urls).extract()

		return (info_names, info_urls)

	def get_db_foreign_key(self, table, query_key):
		'''''获取外键'''
		print("start call get_db_foreign_key...")
		sql = "SELECT id FROM {} WHERE url='{}'".format(table, query_key)
		foreign_key = self.db.fetch_data(sql)

		return foreign_key

	def url_req(this, db_url, scrapy_callback):
		'''''一个具体的页面内 url请求'''
		print("start call url_req...")
		url = "https://{}{}".format(ApiSpider.allowed_domains[0], db_url)
		print("yield scrapy request: {}".format(url))
		yield scrapy.Request(api_url, callback=scrapy_callback)







