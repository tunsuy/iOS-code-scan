# -*- coding: utf-8 -*-

import os
import sys

sys.path.append("/Users/tunsuy/Documents/ScrapyProjects/iOSAPI")

from iOS_proj import Scan

def main():
	scan_path = "/Users/tunsuy/Documents/iOS/MOA/MOA"
	# scan_path = "/Users/tunsuy/Documents/iOS/MOA/MOA/Models/HelpClass/GetIPAddress.m"
	record_file = "./record_err.txt"

	if os.path.isfile(record_file):
		os.remove(record_file)

	scan = Scan(record_file)
	scan.start(scan_path)

if __name__ == '__main__':
	main()