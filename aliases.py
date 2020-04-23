def trim(x):
	for i in ",. -'`":
		x=x.replace(i,'')
	return x.lower()

async def aliases(unit,units,spells):
	unit=trim(unit)
	if unit in ['hoemaster','hoemasters','hoemastersofswordeth']:
		unit='swordmastersofhoeth'
	if unit in ['lsg']:
		unit='lothernseaguard'
	if unit in ['hge']:
		unit='harganethexecutioners'
	if unit in ['bloaty','bloatyboy']:
		unit='bloatedcorpse'
	if unit in ['neverchosen']:
		unit='archaontheeverchosen'
	if unit in ['sos']:
		unit='sistersofslaughter'
	
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