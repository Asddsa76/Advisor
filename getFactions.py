from json import loads
with open('Text files/units.json','rb') as g:
	factions=[]
	for unit in loads(g.read().decode('utf-8')):
		try:
			a=unit['factions'][0]['name_group']
		except:continue
		if a not in factions:
			factions.append(a)
	for i in factions:
		print(i)