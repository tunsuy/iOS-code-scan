
# -*- coding: utf-8 -*-

import sqlite3

from iOSAPI.data_db.abcpool_conn import PoolingConnection

class SQLit3PoolConnection(PoolingConnection):  
    def _create_conn(self, **config):    
        return sqlite3.connect(**config) #关键码实参：必须为字典