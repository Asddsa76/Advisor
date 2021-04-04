from json import loads

def trim(x):
	for i in ",. -'`":
		x=x.replace(i,'')
	return x.lower()

def units(fileName):
	with open('factions.txt','rb') as f:
		factions={}
		for line in f.read().decode('utf-8').split('\n'):
			line=line.split(', ')
			factions[int(line[1].replace('\r',''))]=line[0]
	with open(fileName,'rb') as g:
		units={}
		for unit in loads(g.read().decode('utf-8')):
			if '_summoned' in unit['key']:
				continue
			if not unit['factions']:
				continue
			unitFactions=[i['name_group'] for i in unit['factions']]
			for i in factions:
				if i in unitFactions:
					faction=factions[i]
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
				if unit['damage_mod_'+i]!=0:
					resistances[i]=unit['damage_mod_'+i]
			unit['resistances']=resistances
			unit['name']=faction+' '+unit['name']
			units[trim(unit['name'])]=unit
		return units