def trim(x):
	for i in ",. -'`":
		x=x.replace(i,'')
	return x.lower()

async def aliases(unit,units):
	unit=trim(unit)
	if unit in ['hoemaster','hoemasters','hoemastersofswordeth']:
		return 'swordmastersofhoeth'
	if unit in ['lsg']:
		return 'lothernseaguard'
	if unit in ['hge']:
		return 'harganethexecutioners'
	if unit in ['bloaty','bloatyboy']:
		return 'bloatedcorpse'
	if unit in ['neverchosen']:
		return 'archaontheeverchosen'
	
	for i in units.keys():#Exact match first to not return RoR versions instead of default units, etc.
		if unit==i:
			return i
	for i in units.keys():
		if unit in i:
			return i
	return 404