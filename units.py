from json import loads

def trim(x):
	for i in ",. -'`":
		x=x.replace(i,'')
	return x.lower()

def getFactionIcon(unit):
	with open('Text files/factions.txt','rb') as f:
		factions={}
		for line in f.read().decode('utf-8').split('\n'):
			line=line.replace('\r','').split(', ')
			factions[line[0]]=[line[1]]
			if len(line)==3:
				factions[line[0]].append(int(line[2]))

	unitFactions=[i['name_group'] for i in unit['factions']]
	for unitFaction in unitFactions:
		for faction in factions:
			if unitFaction in factions[faction]:
				return faction

def units(fileName):
	with open(fileName,'rb') as g:
		units={}
		for unit in loads(g.read().decode('utf-8')):
			if '_summoned' in unit['key']:
				continue
			if not unit['factions']:
				continue
			faction=getFactionIcon(unit)

			for i in ['abilities','spells']:
				unit[i]=[j['name'] for j in unit[i]]
				if not unit[i]:
					del unit[i]
			unit['attributes']=[j['key'].capitalize().replace('Guerrilla','Vanguard').replace('Charge_reflector_vs_large','Charge defence').replace('Charge_reflector','Expert_charge_defence').replace('_',' ') for j in unit['attributes']]
			if not unit['attributes']:
				del unit['attributes']
			unit['missile_parry']=unit["parry_chance"]
			resistances={}
			for i in ['flame','magic','physical','missile','all']:
				if unit['damage_mod_'+i] not in [0, None]:
					resistances[i]=unit['damage_mod_'+i]
			unit['resistances']=resistances
			unit['name']=faction+' '+unit['name']
			trimmedName=trim(unit['name'])
			units[trimmedName]=unit
		return units