# -*- coding: utf-8 -*-

from iOSAPI.data_db.sqlite_handler import IOSAPIdb

class ApiVersionInspect(object):
	""" api版本信息类 """
	def __init__(self):
		self.db = IOSAPIdb()
		self.db.set_cursor()

		apiV7 = {
			"systemV": "iOS 7.0+",
			"userV": "ISIOS7"
		}
		apiV8 = {
			"systemV": "iOS 8.0+",
			"userV": "ISIOS8"
		}
		apiV9 = {
			"systemV": "iOS 9.0+",
			"userV": "ISIOS9"
		}
		apiV10 = {
			"systemV": "iOS 10.0+",
			"userV": "ISIOS10"
		}

		self.apiV = [apiV7, apiV8, apiV9, apiV10]

	def get_api_systemV(self, api_name):
		sql = "SELECT sdk FROM objcApi WHERE name='{}'".format(api_name)
		api_sdk = self.db.fetchall_data(sql)
		return api_sdk