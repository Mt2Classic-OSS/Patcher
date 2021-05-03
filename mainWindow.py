#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QToolTip, QPushButton, QComboBox, QMessageBox, QDesktopWidget, QProgressBar, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy, QMenu, QAction
from PyQt5.QtGui import QIcon, QPalette, QBrush, QImage, QPixmap, QFont, QCursor
from PyQt5.QtCore import Qt, QSize
from patcher import Patcher, PatcherCommunication
from subprocess import call, Popen
import os
from config import Config
import configManager
import functools

class MainWindow(QMainWindow):
	logger = None
	patcherThread = None
	patchRunning = True
	def __init__(self):
		QMainWindow.__init__(self) 
		
		self.setWindowTitle('ClassicMetin2 - Patcher')
		self.setWindowIcon(QIcon("resources/metin2.ico"))
		configManager.ReadConfig()
		
		self.centerWindow()
	def initialize(self):
		self.createInterface()
		
		self.logger.debug("Patching thread start")	
		self.comm = PatcherCommunication()
		self.comm.enableButtons.connect(self.enableButtons)
		self.comm.disableButtons.connect(self.disableButtons)
		self.comm.progressTotal.connect(self.setTotalProgress)
		self.comm.progressCurrent.connect(self.setCurrentProgress)
		self.comm.statusTotal.connect(self.setTotalAction)
		self.comm.statusCurrent.connect(self.setCurrentAction)
		self.comm.finished.connect(self.terminatePatcher)
		#self.comm.shopDataLoaded.connect(self.onShopDataLoaded)
		#self.comm.newsDataLoaded.connect(self.onNewsDataLoaded)
		
		if not Config.skipPatch:
			self.patcherThread = Patcher(self.comm)
			self.patcherThread.setLogger(self.logger)
			self.patcherThread.start()
		else:
			self.CurrentLabel.setText("Idle.")
			self.TotalLabel.setText("Can't patch while a client is running.")
	def setLogger(self, logger):
		self.logger = logger
		self.logger.debug("Logger -> Window")
	def createInterface(self):
		self.logger.debug("Creating UI")
		self.setObjectName("MainWindow")
		WINDOW_WIDTH = 1024
		WINDOW_HEIGHT = 576
		self.WINDOW_WIDTH = WINDOW_WIDTH
		self.WINDOW_HEIGHT = WINDOW_HEIGHT
		self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
		
		# BgOverlay
		bgOverlay = QLabel()
		bgOverlay.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
		bgOverlay.move(0, 0)
		bgOverlay.setObjectName("BgOverlay")		
		bgOverlay.setParent(self)		
		self.bgOverlay = bgOverlay
		# LinePattern
		linePatternTop = QLabel()
		linePatternTop.resize(WINDOW_WIDTH, 46)
		linePatternTop.move(0, 0)
		linePatternTop.setObjectName("LinePatternTop")
		linePatternTop.setParent(self)
		self.linePatternTop = linePatternTop
		linePatternBottom = QLabel()
		linePatternBottom.resize(WINDOW_WIDTH, 46)
		linePatternBottom.move(0, WINDOW_HEIGHT - 40)
		linePatternBottom.setObjectName("LinePatternBottom")		
		linePatternBottom.setParent(self)
		self.linePatternBottom = linePatternBottom
		baseX = 0
		baseY = 0
		# ButtonLogo
		ButtonLogo = QPushButton('', self)
		ButtonLogo.setObjectName("ButtonLogo")
		ButtonLogo.resize(420, 201)
		ButtonLogo.move( WINDOW_WIDTH / 2 - 200, 45)
		ButtonLogo.setParent(self)
		self.ButtonLogo = ButtonLogo
		
		# UIBG
		UIBG_WIDTH = 700
		UIBG_HEIGHT = 260
		uiBG = QLabel()
		uiBG.resize(UIBG_WIDTH, UIBG_HEIGHT)
		uiBG.move(WINDOW_WIDTH / 2 - UIBG_WIDTH / 2, 250)
		uiBG.setObjectName("UiBG")		
		uiBG.setParent(self)		
		self.uiBG = uiBG		
		# LanguagePicker
		LP_WIDTH = 130
		languagePicker = QComboBox()
		languagePicker.setObjectName("LanguagePicker")
		languagePicker.resize(LP_WIDTH, 32)
		languagePicker.setParent(self.uiBG)
		languagePicker.move(15, UIBG_HEIGHT - 32 - 10) 
		languagePicker.addItems(configManager.languages)
		languagePicker.setEditable(False)

		for i in range(len(configManager.languages)):
			icon = QIcon(configManager.languageIcons[i])
			languagePicker.setItemIcon(i, icon)
		selectedLanguage = configManager.Get("LOCALE", 0)
		if selectedLanguage >= len(configManager.languages):
			selectedLanguage = 0
		languagePicker.setCurrentIndex(selectedLanguage)
		languagePicker.currentIndexChanged.connect(self.onLanguageChange)
		self.languagePicker = languagePicker
				
		# ButtonStart
		ButtonStart = QPushButton('', self)
		ButtonStart.setObjectName("ButtonStart")
		ButtonStart.setToolTip('Start ClassicMetin2!')
		ButtonStart.resize(300, 68)
		ButtonStart.move( UIBG_WIDTH / 2 - 150, 180)
		ButtonStart.setParent(self.uiBG)
		ButtonStart.clicked.connect(self.openGame)
		#ButtonStart.hide()
		self.ButtonStart = ButtonStart
		
		# CurrentProgress
		CurrentProgress = QProgressBar(self)
		CurrentProgress.setValue(0)
		CurrentProgress.setAlignment(Qt.AlignCenter)
		CurrentProgress.resize(600, 40)
		CurrentProgress.move(UIBG_WIDTH/2 - 300, 40)
		CurrentProgress.setParent(self.uiBG)
		self.CurrentProgress = CurrentProgress
		# CurrentLabel
		CurrentLabel = QLabel(self)
		CurrentLabel.setText("Current Status")
		CurrentLabel.setObjectName("CurrentLabel")
		CurrentLabel.move(UIBG_WIDTH/2-300, 20)		
		CurrentLabel.resize(412, 20)
		CurrentLabel.setParent(self.uiBG)		
		self.CurrentLabel = CurrentLabel

		# TotalProgress
		TotalProgress = QProgressBar(self)
		TotalProgress.setValue(0)
		TotalProgress.setAlignment(Qt.AlignCenter)
		TotalProgress.resize(600, 40)
		TotalProgress.move(UIBG_WIDTH/2 - 300, 117)
		TotalProgress.setParent(self.uiBG)	
		self.TotalProgress = TotalProgress	
		#TotalLabel
		TotalLabel = QLabel(self)
		TotalLabel.setText("Global Status")
		TotalLabel.setObjectName("TotalLabel")
		TotalLabel.resize(412,20)
		TotalLabel.move(UIBG_WIDTH/2 - 300, 97)
		TotalLabel.setParent(self.uiBG)			
		
				
		self.TotalLabel = TotalLabel		
		# ButtonSettings
		ButtonSettings = QPushButton('', self)
		ButtonSettings.setObjectName("ButtonSettings")
		ButtonSettings.setToolTip('Open client options')
		ButtonSettings.setParent(self.uiBG)
		ButtonSettings.resize(32, 32)
		ButtonSettings.move( UIBG_WIDTH - 45, UIBG_HEIGHT - 40)
		
		ButtonSettings.clicked.connect(self.openConfig)
		self.ButtonSettings = ButtonSettings
		# ButtonRepair
		ButtonRepair = QPushButton('', self)
		ButtonRepair.setObjectName("ButtonRepair")
		ButtonRepair.setToolTip('Repair the Client')
		ButtonRepair.setParent(self.uiBG)
		ButtonRepair.resize(32, 32)
		ButtonRepair.move( UIBG_WIDTH - 45 - 40, UIBG_HEIGHT - 40)
		
		ButtonRepair.clicked.connect(self.onRepair)
		self.ButtonRepair = ButtonRepair
		# VersionLabel
		VersionLabel = QPushButton("Patcher v1.%d" % Config.currentVersion, self)
		VersionLabel.setObjectName("VersionLabel")
		VersionLabel.move( WINDOW_WIDTH - 100 ,  3)		
		VersionLabel.resize(100, 40)
		VersionLabel.setParent(self)		
		self.VersionLabel = VersionLabel		
		self.VersionLabel.clicked.connect(self.openContextMenu)	
		try:
			font = QFont("Tahoma", 9)
			font.setStyleStrategy(QFont.NoAntialias)
			QApplication.setFont(font)
			
			styleSheetFile = open("resources/style.css", "r")
			styleSheet = styleSheetFile.read()
			styleSheetFile.close()
			
			self.setStyleSheet(styleSheet)
			#self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
			#self.setAttribute(Qt.WA_NoSystemBackground, True)
			#self.setAttribute(Qt.WA_TranslucentBackground, True)
		except:
			self.logger.exception("Unable to initialize the UI")
			pass
	def openContextMenu(self):
		menu = QMenu(self)
		syserr = QAction("Show syserr.txt", self)
		patch = QAction("Show patch.log", self)
		screensot = QAction("Show screenshot folder", self)
		syserr.triggered.connect(self.showSyserr)
		patch.triggered.connect(self.showPatchLog)
		menu.addAction(syserr)
		menu.addAction(patch)
		menu.popup(QCursor.pos())
	def showScreenshot(self,q):
		Popen("explorer.exe \".\\screenshot\"")
	def showSyserr(self,q):
		Popen("notepad.exe \".\\syserr.txt\"")
	def showPatchLog(self,q):
		Popen("notepad.exe \".\\patch.log\"")
	def onLoadUrl(self, url):
		Popen("explorer %s" % url)
	def onRepair(self):
		reply = QMessageBox.question(self, 'ClassicMetin2',
			"Repairing the client checks for each file's integrity!<br />Do a repair only if you're experiencing trouble with the client!<br /><i>Do you want to coninue?</i>", QMessageBox.Yes | 
			QMessageBox.No, QMessageBox.No)
		
		if reply == QMessageBox.Yes:
			self.logger.info("Closing for Repair")
			try:
				call("repairclient.bat")
			except:
				reply = QMessageBox.critical(self, "Error", "Unable to start the repair.")	
	def openConfig(self):
		if os.path.isfile("config.exe"):
			call("config.exe")
		else:
			reply = QMessageBox.critical(self, "Error", "Unable to open config.")
	def onLanguageChange(self, value):
		if value >= len(configManager.languages):
			value = 0
		configManager.Set("LOCALE", value)
	def openGame(self):
		if os.path.isfile("metin2client.exe"):
			Popen("metin2client.exe")
		else:
			reply = QMessageBox.critical(self, "Error", "Unable to open the client.")	
	def setCurrentProgress(self, value):
		self.CurrentProgress.setValue(value)
	def setTotalProgress(self, value):
		self.TotalProgress.setValue(value)
	def setCurrentAction(self, text):
		self.CurrentLabel.setText(text)
	def setTotalAction(self, text):
		self.TotalLabel.setText(text)
	def disableButtons(self):
		self.ButtonStart.hide()
	def enableButtons(self):
		self.ButtonStart.show()
	def terminatePatcher(self):
		self.patchRunning = False
		self.patcherThread.terminate()
		self.patcherThread.wait()
	def centerWindow(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())
	def closeEvent(self, event):
		if self.patchRunning:
			reply = QMessageBox.question(self, 'ClassicMetin2',
				"The Patch is still running!<br /><i>Are you sure you want to exit?</i>", QMessageBox.Yes | 
				QMessageBox.No, QMessageBox.No)
			
			if reply == QMessageBox.Yes:
				self.logger.info("User exit")
				event.accept()
			else:
				event.ignore() 
		else:
			self.logger.info("User exit")
			event.accept()
	offset = None
	def mousePressEvent(self, event):
		self.offset = event.pos()
	def mouseReleaseEvent(self, event):
		self.offset = None
	def mouseMoveEvent(self, event):
		if self.offset != None:
			x=event.globalX()
			y=event.globalY()
			x_w = self.offset.x()
			y_w = self.offset.y()
			self.move(x-x_w, y-y_w)