
# -*- coding: utf-8 -*-

import time
from queue import Queue

from iOSAPI.data_db.sqlitepool_conn import SQLit3PoolConnection

'''''备注：
	一个连接池拥有多个连接，而每个连接又拥有这个连接池的实例(一个叫pool的属性)
'''

class PoolException(Exception):  
    pass  
  
class Pool(object):  
    '''''一个数据库连接池'''

    dbcs = {"SQLite3":SQLit3PoolConnection}

    def __init__(self, maxActive=5, maxWait=None, init_size=0, db_type="SQLite3", **config):  
        self.__freeConns = Queue(maxActive)  
        self.maxWait = maxWait  
        self.db_type = db_type  
        self.config = config   #数据库相关配置
        if init_size > maxActive:  
            init_size = maxActive  
        for i in range(init_size):  
            self.free(self._create_conn())  #创建指定个数的db连接并放入连接池
      
    def __del__(self):  #定义了__del__方法的话，在对象的引用记数为0时会自动调用__del__方法
        print("__del__ Pool..")  
        self.release()  
      
    def release(self):  
        '''''释放资源，关闭池中的所有连接'''  
        print("release Pool..")  
        while self.__freeConns and not self.__freeConns.empty():  
            con = self.get()  
            con.release()  
        self.__freeConns = None  
  
    def _create_conn(self):  
        '''''创建连接 '''  
        if self.db_type in Pool.dbcs:  #db类型是否在指定的db类型字典中
            return Pool.dbcs[self.db_type](**self.config);  #返回该db类的一个对象
          
    def get(self, timeout=None):  
        '''''获取一个连接 
        @param timeout:超时时间 
        '''  
        if timeout is None:  
            timeout = self.maxWait  
        conn = None  
        if self.__freeConns.empty():#如果容器是空的，直接创建一个连接  
            conn = self._create_conn()  
        else:  
            conn = self.__freeConns.get(timeout=timeout)  
        conn.pool = self   #每次从池中获取连接的时候将连接的pool设置为当前实例
        return conn  
      
    def free(self, conn):  
        '''''将一个连接放回池中 
        @param conn: 连接对象 
        '''  
        conn.pool = None    #在归还这个连接的时候再将其设置为None
        if(self.__freeConns.full()):#如果当前连接池已满，直接关闭连接  
            conn.release()  
            return  
        self.__freeConns.put_nowait(conn)  
          




