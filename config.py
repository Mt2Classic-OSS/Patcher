#!/usr/bin/python
class Config:
	currentVersion = 11
	gameBinArgs = "";
	versionLink = "https://mt2classic.com"
	maxNetworkRetries = 3
	
	configBinName = "config.exe"
	gameBinName = "metin2client.exe"

	patchFileUrls = (
		"http://rest.s3for.me/classic-patch/patchlist",
	);

	tempPatchFilePath = "newpatch.exe"
	tempPatchScriptPath = "newpatch.bat"
	clientRepair = False
	skipPatch = False
	ePackExtension = ".epk"
	eIndexExtension = ".eix"