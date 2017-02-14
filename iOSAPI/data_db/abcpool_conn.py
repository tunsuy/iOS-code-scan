
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod  #导入抽象类
  
class PoolingConnection(object, metaclass=ABCMeta):  
    def __init__(self, **config):  
        self.conn = None  
        self.config = config  
        self.pool = None  
          
    def __del__(self):  #析构函数，自动调用
        self.release()  
          
    def __enter__(self):  #该方法在with语句体执行之前进入运行时上下文（执行）
        pass  
      
    def __exit__(self, exc_type, exc_value, traceback):  #该方法在with语句体执行之后进入运行时上下文（执行）
        self.close()  
          
    def release(self):  
        print("release PoolingConnection..")  
        if(self.conn is not None):  
            self.conn.close()  
            self.conn = None  
        self.pool = None  
              
    def close(self):  
        if self.pool is None:  
            raise PoolException("连接已关闭")  
        self.pool.free(self)  
          
    def __getattr__(self, val):  
        if self.conn is None and self.pool is not None:  
            self.conn = self._create_conn(**self.config)  
        if self.conn is None:  
            raise PoolException("无法创建数据库连接 或连接已关闭")  
        return getattr(self.conn, val)  
 
    @abstractmethod  
    def _create_conn(self, **config):  
        pass 
