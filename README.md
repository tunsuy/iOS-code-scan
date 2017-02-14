# iOS-code-scan

## 简介：
该项目是对ios项目代码进行扫描，发现其是否有代码层面的bug  
目前第一版支持了api版本控制的扫描检查  
后续将逐渐支持其他方面的代码检查，比如是否有内存溢出，数组越界等，支持检查项可配置  

### 下面只对api版本控制检查进行实现讲解

## 思路：
扫描ios项目，将所有的api调用依次提取出来，跟ios官方定义的版本进行比对，  
检查对那些有版本限制的api，在代码中是否有相应的条件判断  

### 那么这就涉及到如下几个问题
1、需要知道ios库中所有的api版本信息情况  
2、需要提取出代码中所有的api调用并重新组装成方法原型  
3、需要知道该方法原型调用是否在相应的条件判断中  
4、条件判断可能是多层嵌套的  
5、方法调用可能特别复杂，跨度可能特别大  
6、方法调用可能是多层嵌套的  

## 解决方案如下：
1、使用爬虫将ios库的api版本信息抓取下来，并存储在数据库中  
——主要定义三个表：framework、class、api  
2、逐个文件逐行扫描，以方法调用的固有特征（[class1 fun_1.1:[class2 fun_2] fun_1.2:xx]），提取出方法原型  
——当然要完整的一个不漏的提取出所有方法，处理逻辑还是很复杂的：使用了栈的数据结构，"[]"的一一对应等逻辑  
3、跟进方法原型读取api数据库，获取其对应的sdk版本  
4、如果有版本限制，则检查其是否处于if条件判断中  
——需要保持if的上下文信息，多层if嵌套的匹配等

### 爬虫：使用了python的scrapy
#### 备注：
1、scrapy startproject ScrapyIOSAPI—创建一个爬虫项目  
2、scrapy shell "https://developer.apple.com/reference?language=objc"—shell调试方法  
——eg: response.xpath('//div[@class="task-symbols"]/div[@class="symbol clm"]/a/code/text()')  
3、scrapy crawl spider_name—执行

### 数据库：sqlite轻量级数据库

## 对ios代码规范的建议：
对于版本控制，统一使用宏定义  
代码不要一行写多条语句，尽量按照ios开发规范来写代码



