#!/usr/bin/python
# -*- coding: utf-8 -*-
try:
	import sys
	from PyQt5.QtWidgets import QApplication, QWidget
	from threading import Thread
	import logging
	import traceback
	import math
	# Internal
	from config import Config
	from mainWindow import MainWindow
	# This is the static entrypoint
	from filelock import FileLock
	try:
		with FileLock("ClassicMetin2.lock"):
			# work with the file as it is now locked
			print("Lock acquired.")
	except IOError:
		# another instance is running
		sys.exit(0)


	if __name__ == '__main__':
		logger = logging.getLogger("ClassicLog")
		ch = logging.FileHandler("patch.log", mode='w')
		
		formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(funcName)s\t%(message)s')

		# add formatter to ch
		ch.setFormatter(formatter)
		
		# add ch to logger
		logger.addHandler(ch)
		logger.setLevel(logging.DEBUG)	
		# 'application' code
		logger.info("ClassicMetin2 Patcher log:")
		logger.info("Version: 1.%d" % Config.currentVersion)
		
		try:		
			if len(sys.argv) > 1:
				logger.info(sys.argv[1])
				if sys.argv[1] == "repair":
					logger.info("Repairing client")
					Config.clientRepair = True
				elif sys.argv[1] == "clean":
					logger.info("Cleaning stuff")
					if os.path.isfile(Config.tempPatchFilePath):
						os.remove(Config.tempPatchFilePath)
					if os.path.isfile(Config.tempPatchScriptPath):
						os.remove(Config.tempPatchScriptPath)
			logger.debug("Loading UI")
			application = QApplication(sys.argv) 
			window = MainWindow()
			
			window.setLogger(logger)
			
			
			
			window.initialize()
			
			
			
			logger.debug("Showing UI")
			window.show() 
			application.exec_() # Modal i guess?
		except SystemExit:
			logger.critical("Closing Patch.")
		except:
			logger.exception("Global Exception catched.")
			raise
except:
	import ctypes
	import sys
	type, value, traceback = sys.exc_info()
	ctypes.windll.user32.MessageBoxW(0,  "%s %s %s" % (type, value, traceback), "Critical Error", 1)