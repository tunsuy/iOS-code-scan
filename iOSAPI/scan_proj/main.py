# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(sys.path[0])))

from iOS_proj import Scan

def main():
	if len(sys.argv) != 3:
		print("请输入需要扫描的文件或目录 和 结果保存文件")
		print("eg: python main.py xx/MOA xx/record_err.txt")
		sys.exit(0)

	scan_path = sys.argv[1]
	# scan_path = "/Users/tunsuy/Documents/iOS/MOA/MOA/Models/HelpClass/GetIPAddress.m"
	record_file = sys.argv[2]

	if os.path.isfile(record_file):
		os.remove(record_file)

	scan = Scan(record_file)
	scan.start(scan_path)

if __name__ == '__main__':
	main()