#!/usr/bin/python
class Config:
	currentVersion = 12
	gameBinArgs = "";
	versionLink = "https://mt2classic.com"
	maxNetworkRetries = 3
	
	configBinName = "config.exe"
	gameBinName = "metin2client.exe"

	patchFileUrls = (
		"http://s3.tebi.io/classic-patch/patchlist",
	);

	tempPatchFilePath = "newpatch.exe"
	tempPatchScriptPath = "newpatch.bat"
	clientRepair = False
	skipPatch = False
	ePackExtension = ".epk"
	eIndexExtension = ".eix"
