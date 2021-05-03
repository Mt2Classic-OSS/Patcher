#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import Config
from threading import Thread
from PyQt5 import QtCore, QtGui
from subprocess import call
from bz2 import BZ2Decompressor
import os
import time
from requests import get
from urllib import request
from zlib import crc32

class PatcherCommunication(QtCore.QObject):
	progressTotal = QtCore.pyqtSignal(int)
	progressCurrent = QtCore.pyqtSignal(int)
	statusTotal = QtCore.pyqtSignal(str)
	statusCurrent = QtCore.pyqtSignal(str)
	enableButtons = QtCore.pyqtSignal()
	disableButtons = QtCore.pyqtSignal()
	finished = QtCore.pyqtSignal()
	newsDataLoaded = QtCore.pyqtSignal(dict)
class Patcher(QtCore.QThread):
	logger = None
	patchFile = None
	comm = None

	def __init__(self, comm):
		QtCore.QThread.__init__(self)
		self.comm = comm
	def __del__(self):
		self.wait()
	def setLogger(self, logger):
		self.logger = logger
		self.logger.info("Logger -> Patcher")
	def run(self):
		self.comm.disableButtons.emit() # Prevent UI interactions
		self.comm.statusTotal.emit("Checking updates.")
		self.comm.statusCurrent.emit("Obtaining version file.")
		
		self.logger.info("Downloading patchlist...")

		# Attempt to fetch a mirror from config
		for mirror in Config.patchFileUrls:
			self.logger.info("Downloading patchlist from da %s" % mirror)
			self.patchFile = self.getPatchFile(mirror)
			if self.patchFile:
				break
		if not self.patchFile:
			return self.abort("Unable to download patchlist")
		
		self.logger.info("Patchlist downloaded!")
		
		self.comm.statusTotal.emit("Checking patcher updates.")
		self.logger.info("Checking patcher updates.")
		
		newVersion = int(self.getRemove("Version"))
		remotePatchUrl = self.getRemove("NewPatchUrl")
		remoteScriptUrl = self.getRemove("NewScriptUrl")
		self.logger.info("Current version %d, server version %d" % (Config.currentVersion, newVersion))
		self.updateMySelf(newVersion, remotePatchUrl, remoteScriptUrl)
		
		# Patch per-se
		self.comm.statusTotal.emit("Checking client updates.")
		self.logger.info("Checking client updates.")		
		
		self.updateFiles(self.getRemove("PatchUrl"))
		
		
		# End
		self.comm.statusCurrent.emit("Idle.")
		self.comm.statusTotal.emit("Update done. Press Start to play!")
		self.comm.progressTotal.emit(100)
		self.comm.progressCurrent.emit(100)
		self.comm.enableButtons.emit()
		self.logger.info("Patching done!")
		self.comm.finished.emit()
	def updateMySelf(self, newVersion, remotePatchUrl, remoteScriptUrl):
		if Config.currentVersion >= newVersion:
			self.logger.info("No new version available!")
		else:
			self.comm.statusTotal.emit("New version available: %d" % newVersion)
			self.logger.info("New version available: %d" % newVersion)
			self.downloadFile(remotePatchUrl + ".bz", Config.tempPatchFilePath + ".bz", 0, True)
			self.downloadFile(remoteScriptUrl + ".bz", Config.tempPatchScriptPath + ".bz", 0, True)
			self.sleep(1)
			call(Config.tempPatchScriptPath)
	def updateFiles(self, currentMirror):
		downloadQueue = []
		self.comm.statusTotal.emit("Checking file version")		
		self.logger.info("Checking file version")		
		for fileName, version in self.patchFile.items():
			if fileName.endswith(Config.ePackExtension) and not Config.clientRepair: # TODO Integrity check
				continue
			version = version.strip().replace('\n','').replace('\r','')
			our_version = "Not found"
			if os.path.isfile(fileName):
				our_version = self.getCRC32(fileName)
			if our_version != version:
				self.logger.info("%s needs an update! (server: %s - local: %s)" % (fileName, version, our_version))
				baseName, extension = os.path.splitext(fileName)
				if extension == ".exe" or extension == ".dll" or extension == ".bat" or extension == Config.ePackExtension:
					fileName += ".bz"
				elif extension == Config.eIndexExtension and not Config.clientRepair: # And not doing integrity check
					downloadQueue.append(baseName + Config.ePackExtension + ".bz")
				downloadQueue.append(fileName)	
		totalCount = len(downloadQueue)
		currentCount = 0				
		for fileName in downloadQueue:
			currentCount += 1
			percentage = int(float(currentCount) / float(totalCount) * 100.0)
			if percentage > 100:
				percentage = 100
			self.comm.progressTotal.emit(percentage)
			self.comm.statusTotal.emit("Updating client: file %d of %d" % (currentCount, totalCount))		
			self.downloadFile(currentMirror + fileName, fileName)
	def getRemove(self, index):
		val = self.patchFile[index]
		if not val:
			return None
		del self.patchFile[index]
		return val.replace("\r", "").replace("\n", "")
	def getPatchFile(self, mirror):
		ret = {}
		rawFile = self.downloadString(mirror)
		if rawFile == "" or rawFile == None:
			return None
		for line in rawFile.split("\n"):
			if not line.strip():
				continue
			split = line.split("\t")
			if len(split) < 2:
				continue
			ret.update({split[0]: split[1]})
		return ret
	def downloadString(self, remote):
		try:
			return request.urlopen(remote).read().decode('utf-8')
		except:
			self.logger.exception("Unable to download %s" % remote)
			return ""
	def downloadFile(self, remote, local, attempts = 0, forceExtract = False):
		try:
			os.makedirs(os.path.dirname("./" + local), exist_ok=True)
			if attempts > 0:
				self.logger.info("Downloading %s from %s, attempt %d" % (local, remote, attempts))
			self.comm.progressCurrent.emit(0)
			with open(local, 'wb') as f:
				start = time.time()
				r = get(remote, stream=True)
				total_length = None
				try:
					total_length = int(r.headers.get('content-length'))
				except:
					pass
				dl = 0
				if total_length is None:
					f.write(r.content)
				else:
					for chunk in r.iter_content(1024):
						dl += len(chunk)
						f.write(chunk)
						try:
							done = int(50 * dl / total_length)
							bps = float(dl//(time.time() - start))
							mesaure = "B"
							if bps > 1024:
								bps /= 1024.0
								measure = "KB"
							if bps > 1024:
								bps /= 1024.0
								measure = "MB"						
							self.comm.statusCurrent.emit("Downloading %s. Speed %.3f %s/s" % (local, bps, measure))
							percentage = int(float(dl) / float(total_length) * 100) 
							if percentage > 100:
								percentage = 100
							self.comm.progressCurrent.emit(percentage)
						except:
							pass
				f.close()
				if forceExtract or local[-3:] == ".bz":
					
					
					self.comm.statusCurrent.emit("Extracting %s..." % local)
					self.bz2Decompress(local)
				return True
		except Exception:
			if attempts > Config.maxNetworkRetries:
				self.logger.exception("Unable to download: %s" % remote)
				return self.abort("Unable to download: %s" % remote)
			else:
				self.downloadFile(remote, local, attempts + 1, forceExtract)
	def bz2Decompress(self, path):
		try:
			bufsize = 1024
			chunkcount = 0
			newfilepath = os.path.join(path.replace(".bz", ""))
			decompressor = BZ2Decompressor()
			with open(newfilepath, 'wb') as new_file, open(path, 'rb') as file:
				self.logger.debug("Decompressing %s" % path)
				while True:
					chunkcount += 1
					chunk = file.read(1024)
					if not chunk:
						break
					dec_chunk = decompressor.decompress(chunk)
					new_file.write(dec_chunk)
			os.remove(path)
		except:
			self.logger.exception("Unable to extract %s" % path)
			self.abort("Unable to extract %s" % path)
	def abort(self, reason):
		#TODO Message
		self.logger.critical(reason)
		self.comm.enableButtons.emit()
		self.comm.finished.emit()
		return False
	def getCRC32(self, fileName):
		prev = 0
		for eachLine in open(fileName,"rb"):
			prev = crc32(eachLine, prev)
		return ("%X"%(prev & 0xFFFFFFFF)).lower().rjust(8, '0')