# -*- coding: utf-8 -*-

import os
import sys
import re

from opr_helper import Stack, ExtString, FileDirHandler
from apiV_inspect import ApiVersionInspect
from queue import Queue

class Scan(object):
	"""docstring for Scan"""

	line_placeholder = "placeholder"
	
	def __init__(self, record_file):
		self.square_bracket_left_index_stack = Stack()  #"["桟存储，先进后出
		self.brace_left_index_stack = Stack()  #"{"桟存储
		self.if_line_list = []   #"if"行 list存储
		self.if_index_stack = Stack()  # "if"开始的行索引位置
		# self.square_bracket_right_index_queue = Queue()  #"]"队列存储，先进先出
		self.ext_string = ExtString()
		self.file_dir_handler = FileDirHandler()
		self.api_ver_inspect = ApiVersionInspect()

		self.record_file = record_file

	def handler_file(self, file):
		print("start scan file: {}".format(file))

		ext_name = os.path.splitext(file)[1]
		if ext_name != ".m" and ext_name != ".mm":
			print("该文件不是 .m 或者 .mm 后缀的文件，不处理")
			return

		if os.path.isfile(file) == False:
			print("handler_file argv must is file type")
			return

		self.whole_line = ""   #真正完整的ios一行代码
		self.line_num = 0     #记录文件行数
		self.if_whole_content = ""

		for line in open(file):
			self.line_num += 1

			#去掉注释代码
			comment_code_index = line.find("//")
			not_comment_code = line[:comment_code_index].strip()

			self.opr_if_whole_content(not_comment_code)

			self.whole_line += " " + not_comment_code

			#将一行中所有的"]"所在位置放入队列
			# for next_index in self.ext_string.find_char_next(line, "]"):
			# 	self.square_bracket_right_index_queue.enqueue(next_index)

			# if self.square_bracket_right_index_queue.isEmpty():
			# 	continue

			#取出一个"]"，并对其之前的文本进行处理
			# square_bracket_right_index = self.square_bracket_right_index_stack.dequeue()

			if self.is_not_fun_call():
				#print("start a new whole_line scan...")
				self.whole_line = ""
				#self.line_num += 1

			elif self.is_only_square_bracket_left():
				#多行调用，直接不处理，跳到下一次循环中：将self.whole_line加上下一行的字符串
				print("该行只有'['号，说明是多行调用")
				print("whole_line: {}".format(self.whole_line))

			else:
				self.handler_fun_call(file)
				self.check_end(file)

	################ 方法调用处理部分 start ######################

	def filter_wrong_square_bracket(self):
		"""  过滤其他不属于方法调用的[]字符 """
		square_bracket_right_index = self.whole_line.find("]")
		self.wrong_square_bracket(square_bracket_right_index)

		square_bracket_left_index = self.whole_line.find("[")
		self.wrong_square_bracket(square_bracket_left_index)

	def wrong_square_bracket(self, square_bracket_index):
		""" 不是真正的方法调用[]的字符串处理
			eg: "["等
		"""
		square_bracket_index_before = square_bracket_index - 1
		while square_bracket_index_before >= 0 and self.whole_line[square_bracket_index_before] == " ":
			square_bracket_index_before = square_bracket_index_before - 1

		square_bracket_index_after = square_bracket_index + 1
		while square_bracket_index_after < len(self.whole_line) and self.whole_line[square_bracket_index_after] == " ":
			square_bracket_index_after = square_bracket_index_after + 1

		if square_bracket_index_before < 0 or square_bracket_index_after >= len(self.whole_line):
			return

		elif self.whole_line[square_bracket_index_before] == '"' and self.whole_line[square_bracket_index_after] == '"':
			not_square_bracket_right = self.whole_line[square_bracket_index_before:square_bracket_index_after+1]
			self.whole_line = self.whole_line.replace(not_square_bracket_right, Scan.line_placeholder)

		elif self.whole_line[square_bracket_index_before] == "'" and self.whole_line[square_bracket_index_after] == "'":
			not_square_bracket_right = self.whole_line[square_bracket_index_before:square_bracket_index_after+1]
			self.whole_line = self.whole_line.replace(not_square_bracket_right, Scan.line_placeholder)

	def is_only_square_bracket_left(self):
		""" 判断是否只有"["号 """
		self.filter_wrong_square_bracket()

		square_bracket_right_index = self.whole_line.find("]")
		square_bracket_left_index = self.whole_line.find("[")
		
		if square_bracket_right_index == -1 and square_bracket_left_index != -1:
			return True
		else:
			return False

	def is_not_fun_call(self):
		""" 判断是否都没有"["号和"]"号 """
		self.filter_wrong_square_bracket()

		square_bracket_right_index = self.whole_line.find("]")
		square_bracket_left_index = self.whole_line.find("[")

		if square_bracket_right_index == -1 and square_bracket_left_index == -1:
			#因为self.whole_line是已经替换过的方法调用行，所以即使是多行调用，这个条件判断也是成立的
			return True
		else:
			return False

	def handler_fun_call(self, file):
		""" 对一行中方法调用的处理，每次只处理一个方法调用，得到其方法原型 """
		self.filter_wrong_square_bracket()

		square_bracket_right_index = self.whole_line.find("]")
		line_part = self.whole_line[:square_bracket_right_index+1]

		fun_call_part = self.get_fun_call_part(line_part)
		api_fun = self.get_api_fun(fun_call_part)
		
		self.check_user_api_for_code(file, api_fun)

		self.whole_line = self.whole_line.replace(fun_call_part, Scan.line_placeholder)
		#print("handler_fun_call after - whole_line: {}".format(self.whole_line))

	def check_end(self, file):
		""" 检查一行中的方法调用是否结束，因为有的行可能有多个方法调用 """
		print("check more call for whole_line...")
		if self.is_not_fun_call():
			self.whole_line = ""
			#self.line_num += 1

		elif self.is_only_square_bracket_left():
			print("该行只有'['号，说明是多行调用")

		else:
			self.handler_fun_call(file)

	# def check_end(self, file):
	# 	print("whole_line: {}".format(self.whole_line))
	# 	square_bracket_right_index = self.whole_line.find("]")

	# 	#将"]"之前的所有"["放入桟中
	# 	line_part = self.whole_line[:square_bracket_right_index+1]
	# 	self.square_bracket_left_index_stack.clear()
	# 	for next_index in self.ext_string.find_char_next(line_part, "["):
	# 		self.square_bracket_left_index_stack.push(next_index)

	# 	if square_bracket_right_index == -1 and self.square_bracket_left_index_stack.isEmpty():
	# 		#一个完整的方法调用已完成
	# 		print("一个完整的方法已扫描完成")
	# 		self.whole_line = ""
	# 		self.line_num += 1
	# 		return

	# 	elif square_bracket_right_index == -1 and self.square_bracket_left_index_stack.isEmpty() == False:
	# 		#桟中的"["还没有用完, 而该行以无"]": 说明该方法调用占用多行
	# 		print("该方法占用多行")
	# 		return
	
	# 	elif self.square_bracket_left_index_stack.isEmpty():
	# 		#无与之对应的"[": 说明之前的[]一一对应的判断有误
	# 		print("Bug:'['count is {}- []一一对应的判断有误，请检查".format(self.square_bracket_left_index_stack.size()))
	# 		sys.exit(1)  #退出程序，并返回错误标识

	# 	else:
	# 		print("处理方法调用中的某部分")
	# 		line_part = self.whole_line[:square_bracket_right_index+1]
	# 		fun_call_part = self.get_fun_call_part(line_part)
	# 		api_fun = self.get_api_fun(fun_call_part)
	# 		self.write_file(file, self.line_num, api_fun)

	# 		self.whole_line = self.whole_line.replace(fun_call_part, Scan.line_placeholder)
	# 		self.check_end(file)

	def is_legal_fun_name(self, fun_name):
		""" 判断是不是正确的方法名字
			方法名：只能包含数字、字母、_、$
		"""
		pattern = re.compile(r'^[a-zA-Z0-9_$]+$')
		is_match = pattern.match(fun_name)
		if is_match:
			return True
		else:
			return False

	def get_api_fun(self, fun_call_part):
		""" 将方法调用转换成方法原型
			@param:
			fun_call_part: [class fun_1:xx fun_2:xx] 
			@return:
			fun_1:fun_2: 
		"""
		print("start get_api_fun from: {}".format(fun_call_part))

		fun_components = fun_call_part.split(" ")

		api_fun = ""
		for index in range(1, len(fun_components)):	
			if len(fun_components) == 2:
				#方法调用由2个部分组成，则方法参数可有可无
				if ":" in fun_components[index]:
					fun_component = fun_components[index].split(":")[0]
					api_fun += fun_component + ":"
				else:
					fun_component = fun_components[index]
					api_fun += fun_component[:len(fun_component)-1]

			elif len(fun_components) > 2:
				#方法调用由2个以上部分组成，则每个部分一定有参数
				if ":" in fun_components[index]:
					fun_component = fun_components[index].split(":")[0]
					if self.is_legal_fun_name(fun_component):
						api_fun += fun_component + ":"

		return api_fun

	def get_fun_call_part(self, line_part):
		""" 从方法调用及其之前的文本中获取到方法调用
			@param:
			line_part: [xxxxx [class fun]
			@return:
			[class fun]
		"""
		print("start get_fun_call_part from: {}".format(line_part))

		self.square_bracket_left_index_stack.clear()

		#将"]"之前的所有"["放入桟中
		for next_index in self.ext_string.find_char_next(line_part, "["):
			self.square_bracket_left_index_stack.push(next_index)

		if self.square_bracket_left_index_stack.isEmpty():
			#说明之前的[]一一对应的判断有误
			print("Bug:'['count is {} - '['与']'一一对应的判断有误，请检查".format(self.square_bracket_left_index_stack.size()))
			sys.exit(1)  #退出程序，并返回错误标识

		square_bracket_left_index = self.square_bracket_left_index_stack.pop()  #将之对应的"["出桟
		fun_call_part = line_part[square_bracket_left_index:] #左闭右开区间

		return fun_call_part

	################ 方法调用处理部分 end ######################

	################ if判断处理部分 start ######################

	def opr_if_whole_content(self, line):
		""" 设置if条件判断部分代码 """

		if_index = line.find("if")
		if if_index != -1:
			self.if_index_stack.push(if_index)
			self.if_line_list.append(line)

		if self.if_index_stack.isEmpty() == False:
			#只要if还没有匹配完，就叠加
			self.if_whole_content += " " + line
		else:
			self.if_whole_content = line

		self.if_stack_handler()

	def if_stack_handler(self):
		""" if桟的处理 """
		if self.if_index_stack.isEmpty():
			return

		if_index = self.if_index_stack.peek()
		if if_index == None:
			return

		brace_left_index_stack = Stack()

		brace_right_index = self.if_whole_content.find("}")
		while brace_right_index != -1:
			print("self.if_whole_content: {}".format(self.if_whole_content))
			brace_left_index_stack.clear()
			#将"}"之前的所有"{"放入桟中
			brace_riht_part = self.if_whole_content[:brace_right_index+1]
			for next_index in self.ext_string.find_char_next(brace_riht_part, "{"):
				brace_left_index_stack.push(next_index)

			if brace_left_index_stack.isEmpty():
				#说明之前的{}一一对应的判断有误
				print("self.if_whole_content: {}".format(self.if_whole_content))
				print("Bug: '{'count is {} - '{'与'}'一一对应的判断有误，请检查".format(brace_left_index_stack.size()))
				sys.exit(1)  #退出程序，并返回错误标识

			brace_left_index = brace_left_index_stack.pop()
			if brace_left_index_stack.isEmpty() or (if_index > brace_left_index_stack.peek() and if_index < brace_left_index):
				if self.if_index_stack.isEmpty():
					return
				self.if_index_stack.pop()
				self.if_line_list.pop()

			brace_part = self.if_whole_content[brace_right_index:brace_right_index+1]
			self.if_whole_content = self.if_whole_content.replace(brace_part, Scan.line_placeholder)

			brace_right_index = self.if_whole_content.find("}")

	def get_brace_right_part(self):
		""" 得到"}"及其之前的代码部分 """

		self.brace_left_index_stack.clear()

		brace_right_index = self.if_whole_content.find("}")
		if brace_right_index != -1:
			#将"}"之前的所有"{"放入桟中
			brace_riht_part = self.if_whole_content[:brace_right_index+1]
			for next_index in self.ext_string.find_char_next(brace_riht_part, "{"):
				self.brace_left_index_stack.push(next_index)

		#替换掉第一层{}代码部分
		brace_part = self.if_whole_content[self.brace_left_index_stack.pop():brace_right_index+1]
		self.if_whole_content = self.if_whole_content.replace(brace_part, Scan.line_placeholder)

		return brace_riht_part

	def check_user_api_for_code(self, file, api_fun):
		""" 检查代码中api版本判断的使用情况 """

		api_userVs = self.get_userV_from_systemV(api_fun)
		print("api_userVs: {}".format(api_userVs))

		# brace_riht_part = self.get_brace_right_part()
		# if brace_right_index == None:
		# 	return

		# elif (fun_call_part in brace_riht_part) and self.if_stack.isEmpty == True:
		# 	if api_userV is not None:
		# 		#该方法有api版本限制，但是代码中没有if判断
		# 		self.write_file(file, self.line_num, api_fun)
		# 		return
			
		# elif (fun_call_part in brace_riht_part) and self.if_stack.isEmpty == False:
		# 	if api_userV is None:
		# 		#该方法没有版本限制，但是代码中有if判断
		# 		self.write_file(file, self.line_num, api_fun)
		# 		return
		# 	else:
		# 		#该方法有版本限制，代码中有if判断，检查判断是否正确
		# 		api_right_flag = False
		# 		for if_line in if_list:
		# 			if api_userV in if_line:
		# 				api_right_flag = True
		# 				break
		# 		if api_right_flag == False:
		# 			self.write_file(file, self.line_num, api_fun)
		# 		return

		# else:
		# 	self.check_user_api_for_code(api_fun, fun_call_part)

		if self.if_index_stack.isEmpty():
			if api_userVs is not None:
				#该方法有api版本限制，但是代码中没有if判断
				self.write_file(file, self.line_num, api_fun, api_userVs)
			
		else:
			if api_userVs is not None:
				#该方法有版本限制，代码中有if判断，检查判断是否正确
				for if_line in self.if_line_list:
					for api_userV in api_userVs:			
						if api_userV in if_line:
							return

				self.write_file(file, self.line_num, api_fun, api_userVs)

			# else:
			# 	该方法没有版本限制，但是代码中有if判断
			# 	for if_line in self.if_line_list:
			# 		for apiv in self.api_ver_inspect.apiV:
			# 			if apiv["userV"] in if_line:
			# 				self.write_file(file, self.line_num, api_fun)
			# 				break

	################ if判断处理部分 end ######################

	def write_file(self, err_file, err_line, err_fun_call, api_userV):
		""" 将问题调用方法写入文件中 """
		print("write_file for api_fun: {}".format(err_fun_call))
		if err_fun_call == "":
			return
		#print("write_file for api_fun: {}".format(err_fun_call))
		with open(self.record_file, "a") as f:
			f.write("【{}】{}行: {} --> {}\n".format(err_file, err_line, err_fun_call, api_userV))

	def get_userV_from_systemV(self, api_name):
		""" 代码中对应的ios系统版本定义
			ps: 因为不知道这个方法隶属于哪个类，故将所有的方法版本均返回
				如果版本中有一个小于7.0 则直接返回None
			return: 用户定义的ios版本字符串list
		"""
		api_sdks = self.api_ver_inspect.get_api_systemV(api_name)
		if api_sdks == None:
			return
		print("system api_sdks: {}".format(api_sdks))

		api_userVs = []
		for api_sdk in api_sdks:
			sdk_digit = re.findall(r'[\d|.]+', api_sdk[0])
			print("sdk_digit: {}".format(sdk_digit))
			if len(sdk_digit) == 0 or float(sdk_digit[0]) < 7.0:
				return

			for apiv in self.api_ver_inspect.apiV:
				if apiv["systemV"] == api_sdk[0]:
					api_userVs.append(apiv["userV"])
					break

		return api_userVs if len(api_userVs) != 0 else None

	def start(self, scan_path):
		print("start scan ios project...")
		self.file_dir_handler.DFS_Dir(scan_path, fileCallback = self.handler_file)


			
