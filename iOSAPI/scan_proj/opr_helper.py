# -*- coding: utf-8 -*-

import os

class Stack: 
    """模拟栈""" 
    def __init__(self): 
        self.items = [] 

    def isEmpty(self): 
        return len(self.items)==0  

    def push(self, item): 
        self.items.append(item) 

    def pop(self): 
        return self.items.pop()  

    def peek(self): 
        if not self.isEmpty(): 
            return self.items[len(self.items)-1] 

    def size(self): 
        return len(self.items) 

    def clear(self):
        del self.items[:]

class ExtString(object):
    """对现有string接口进行扩展"""
    def __init__(self):
        pass

    def find_char_next(self, str, ch):
        for i, ltr in enumerate(str):
            if ltr == ch:
                yield i

    def find_sub_next(self, str, sub_str):
        offs = -1
        while True:
            offs = str.find(sub_str, offs + 1)
            if offs == -1:
                break
            else:
                yield offs

class FileDirHandler(object):
    """对文件目录的相关操作"""
    def __init__(self):
        pass

    def BFS_Dir(self, path, dirCallback = None, fileCallback = None):
        """广度优先遍历指定目录"""
        print("start BFS_Dir for path: {}".format(path))

        queue = []  
        ret = []  
        queue.append(path);  
        while len(queue) > 0:  
            tmp = queue.pop(0)  
            ret.append(tmp) 

            if(os.path.isdir(tmp)):   
                for item in os.listdir(tmp):  
                    queue.append(os.path.join(tmp, item))  
                if dirCallback:  
                    dirCallback(tmp)  

            elif(os.path.isfile(tmp)):   
                if fileCallback:  
                    fileCallback(tmp) 

        return ret  
      
      
    def DFS_Dir(self, path, dirCallback = None, fileCallback = None):
        """深度优先遍历指定目录"""
        print("start DFS_Dir for path: {}".format(path))
        print("fileCallback: {}".format(fileCallback))

        stack = []  
        ret = []  
        stack.append(path);  
        while len(stack) > 0:  
            tmp = stack.pop(len(stack) - 1)
            ret.append(tmp) 

            if(os.path.isdir(tmp)): 
                for item in os.listdir(tmp):  
                    stack.append(os.path.join(tmp, item))  
                if dirCallback:  
                    dirCallback(tmp)  

            elif(os.path.isfile(tmp)):  
                if fileCallback:
                    fileCallback(tmp)  

        return ret  
            
            