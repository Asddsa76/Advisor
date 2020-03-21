def trim(x):
	for i in ",. -'`":
		x=x.replace(i,'')
	return x.lower()

async def aliases(unit,units,spells):
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
	if unit in ['sos']:
		return 'sistersofslaughter'
	
	output=[]
	for i in units.keys():
		if unit in i:
			output.append(i)
	for i in spells.keys():
		if unit in i:
			output.append(i)
	
	if output:
		output.sort(key=lambda x:len(x))
		return output[:10]
	return 404