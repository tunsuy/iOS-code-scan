# -*- coding: utf-8 -*-

import sqlite3
import os, sys

from iOSAPI.data_db.dbconn_pool import Pool  		

class IOSAPIdb(object):
	pool = None

	db_path = "iOSAPI.db"  #在当前目录下生成数据库文件

	def __init__(self):
		print("start init IOSAPIdb...")
		if IOSAPIdb.pool is None:   
			IOSAPIdb.pool = Pool(database=IOSAPIdb.db_path)
	
	def init_tables(self):
		if os.path.isfile(IOSAPIdb.db_path):
			os.remove(IOSAPIdb.db_path)   
		self.set_cursor()
		self.__create_table()

	def set_cursor(self):
		print("pool: {}".format(IOSAPIdb.pool))
		self.conn = IOSAPIdb.pool.get()

		with self.conn:  #上下文管理器，无论语句体中执行结果如果都能进入__exit__()方法执行
			self.cursor = self.conn.cursor()
			print("conn: {}".format(self.conn))

	def __create_table(self):
		print("start call create table")
		# self.cursor.execute('''CREATE TABLE category
		# 	(id integer primary key autoincrement, 
		# 	 name text)''')    #api分类表

		self.cursor.execute('''CREATE TABLE framework
			(id integer primary key autoincrement, 
			 name text,
			 url text,
			 category text)''')   #api framework表

		self.cursor.execute('''CREATE TABLE class
			(id integer primary key autoincrement, 
			 name text,
			 url text,
			 framework_id integer,
			 FOREIGN KEY(framework_id) REFERENCES framework(id))''')   #class表

		self.cursor.execute('''CREATE TABLE objcApi
			(id integer primary key autoincrement,
			 name text,
			 sdk text,
			 url text,
			 tag text,
			 class_id integer,
			 FOREIGN KEY(class_id) REFERENCES class(id))''')   #api表

	def insert_data(self, sql, data):
		print("start insert data ...")
		print("sql: {}".format(sql))
		print("data: {}".format(data))
		self.cursor.execute(sql, data) #占位符必须为元组
		self.conn.commit()	#更新操作必须提交	
		
	def fetch_data(self, sql):
		print("start fetch data ...")
		print("sql: {}".format(sql))
		self.cursor.execute(sql)
		return self.cursor.fetchone()

	def fetchall_data(self, sql):
		print("start fetch data ...")
		print("sql: {}".format(sql))
		self.cursor.execute(sql)
		return self.cursor.fetchall()

	def update_data(self, sql, data):
		print("start update data ...")
		print("data: {}".format(data))
		print("sql: {}".format(sql))
		self.cursor.execute(sql, data)
		self.conn.commit()







