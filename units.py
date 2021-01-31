from json import loads

def trim(x):
	for i in ",. -'`":
		x=x.replace(i,'')
	return x.lower()

def units(fileName):
	with open(fileName,'rb') as g:
		units={}
		for unit in loads(g.read().decode('utf-8')):
			if '_summoned_' in unit['key']:
				continue
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
			units[trim(unit['name'])]=unit
		return units