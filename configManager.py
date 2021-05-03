#!/usr/bin/python
CONFIG_PATH = "metin2.cfg"

languages = []
languageIcons = []

def loadLanguages():
	global languages
	global languageIcons
	try:
		with open("languages.inf", 'r', encoding='ansi') as f:
			for line in f:
				if '|' in line:
					d = line.split('|')
					languages.append(d[0].strip())
					languageIcons.append("resources/lang/%s.png" % d[1].strip())
	except:
		languages = ["English", "Italian", "Limba română", "Türkçe", "Czech", "Deutsche"]
		languageIcons = ["resources/lang/en.png", "resources/lang/it.png", "resources/lang/ro.png", "resources/lang/tr.png", "resources/lang/cz.png",  "resources/lang/de.png"]
loadLanguages()

configData = {}

def num( s):
	try:
		return int(s)
	except ValueError:
		return float(s)
def ReadConfig():
	global configData
	configData = {}
	try:
		configFile = open(CONFIG_PATH, 'r')
		for line in configFile:
			data = line.split()
			if len(data) < 2:
				print("Wtf?")
			else:
				configData[data[0].strip()] = num(data[1].strip())
				print("Read: %s | %d" % (data[0], configData[data[0]]))
		configFile.close()
	except:
		pass
def SaveConfig():
	configFile = open(CONFIG_PATH, 'w')
	for key, value in configData.items():
		configFile.write("%s\t%s\n" % (key, str(value)))
	configFile.close()
def Get( key, default):
	if not key in configData:
		return default
	return configData[key]
def Set( key, value):
	configData[key] = value
	SaveConfig()