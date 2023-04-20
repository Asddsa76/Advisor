from json import loads

def trim(x):
	for i in ",. -'`":
		x=x.replace(i,'')
	return x.lower()

def spells(fileName):
	with open(fileName,'rb') as h:
		spells={}
		spellJSON=[]
		ocJSON={}
		for spell in loads(h.read().decode('utf-8')):
			if '_bound' in spell['key']:continue#Don't process bound spells
			if spell['name'] in [None, 'placeholder']:continue
			if spell['tooltip']==None:continue
			if '_upgraded' in spell['key'] or 'Master Rune' in spell['name']:#Overcast
				ocJSON[spell['key']]=spell
			else:
				spellJSON.append(spell)

		for spell in spellJSON:
			spellName=trim(spell['name'])
			if spell['has_overcast']==True:
				oc=ocJSON[spell['overpower_option']['key']]
				output='**'+spell['name']+'**: '
				output+='*'+spell['tooltip'].strip()+'*\n'
				spelltype='_'.join(spell['type_key'].split('_')[2:]).replace('_',' ').capitalize()+', '

				spell_sa=spell['special_ability']
				oc_sa=oc['special_ability']
				if spell_sa==None:continue
				basicInfo=[]
				for i in [("mp_cost",' gold'),("mana_cost",' mana'),("target_intercept_range",' meters'),('wind_up_time','s cast time'),("recharge_time",'s recharge')]:
					try:#Warp hunger spells don't have any basic info
						if i[0] in spell_sa.keys():
							if spell_sa[i[0]] in [0,-1]:#Passives
								continue
							if oc_sa[i[0]]==spell_sa[i[0]]:
								basicInfo.append(str(spell_sa[i[0]])+i[1])
							else:
								basicInfo.append(str(spell_sa[i[0]])+' **__'+str(oc_sa[i[0]])+'__**'+i[1])
					except:
						pass
				for i in [('active_time','s duration'),('effect_range','m radius')]:
					try:
						if spell_sa[i[0]] not in [0,-1]:
							if oc_sa[i[0]]==spell_sa[i[0]]:
								basicInfo.append(str(spell_sa[i[0]])+i[1])
							else:
								basicInfo.append(str(spell_sa[i[0]])+' **__'+str(oc_sa[i[0]])+'__**'+i[1])
						elif oc_sa[i[0]] not in [0,-1]:
							basicInfo.append('**__'+str(oc_sa[i[0]])+i[1]+'__**')
					except:pass

				for i in [('num_effected_friendly_units',' max units')]:
					try:
						if spell_sa[i[0]] not in [1,0,-1]:
							if oc_sa[i[0]]==spell_sa[i[0]]:
								basicInfo.append(str(spell_sa[i[0]])+i[1])
							else:
								basicInfo.append(str(spell_sa[i[0]])+' **__'+str(oc_sa[i[0]])+'__**'+i[1])
					except:pass

				
				output+=spelltype+', '.join(basicInfo)
				dicts=['dominant_phase','phase', 'projectile', 'miscast_explosion_contact_phase_effect', 'spawned_unit', 'projectile_explosion_contact__effect', 
				'projectile_explosion', 'bombardment', 'projectile_contact_stat_effect', 'vortex', 'vortex_phase']
				for i in dicts:
					if i in spell.keys():
						x=spell[i]
						y=oc[i]
					elif i in spell_sa.keys():
						x=spell_sa[i]
						y=oc_sa[i]
					else:continue
					if not x:continue

					
					notGarbageInfo=[]#No false booleans or uninteresting strings
					damageBase=x['damage'] if 'damage' in x else 0
					damageAP=x['damage_ap'] if 'damage_ap' in x else 0
					ocBase=y['damage'] if 'damage' in y else 0
					ocAP=y['damage_ap'] if 'damage_ap' in y else 0
					if damageBase or damageAP:
						damageAppend=''
						if damageBase:
							if damageAP:
								damageAppend=str(damageBase+damageAP)+' ('+str(damageBase)+' base + '+str(damageAP)+' AP)'
							else:
								damageAppend=str(damageBase)+' base'
						elif damageAP:
							damageAppend=str(damageAP)+' AP'

						ocAppend=''
						if ocBase:
							if ocAP:
								ocAppend=str(ocBase+ocAP)+' ('+str(ocBase)+' base + '+str(ocAP)+' AP)'
							else:
								ocAppend=str(ocBase)+' base'
						elif ocAP:
							ocAppend=str(ocAP)+' AP'
						if damageAppend==ocAppend:
							notGarbageInfo.append('Damage: '+damageAppend)
						else:
							notGarbageInfo.append('Damage: '+damageAppend+' **__'+ocAppend+'__**')
					for j in x.items():
						if j[0] in ['damage','damage_ap','heal_amount', 'ticks']:continue
						if any(l in j[0] for l in ['expansion_speed','start_radius', 'change_max_angle','move_change_freq','is_magical','duration','elevation','calibration','minimum_range','frequency']):continue
						if any(l in j[0] for l in ['shots_per_volley','projectile_number', 'num_vortexs']) and j[1]==1:continue
						k=y[j[0]]
						dictAppend=''
						ocAppend=''
						if type(j[1])==type(1) and j[1] not in [0,-1]:
							dictAppend=j[0].replace('goal_','')+': '+str(j[1])
						elif type(j[1])==type(0.1):
							dictAppend=j[0]+': '+str(j[1])
						elif j[1]==True:
							dictAppend=j[0]
						elif j[0]=='statEffects' and j[1]:
							dictAppend=', '.join([str(l['value'])+' '+' '.join(l['stat'].split('_')[1:]) for l in j[1]])
						elif j[0]=='attributeEffects' and j[1]:
							dictAppend=', '.join(l['attribute'].replace('_',' ') for l in j[1])
						try:
							if j[1] and 'statEffects' in j[1] and j[1]['statEffects']:
								dictAppend=', '.join([str(l['value'])+' '+' '.join(l['stat'].split('_')[1:]) for l in j[1]['statEffects']])
						except:pass
						#k is just the value, oc version of j[1]. The name of k is equal to j[0]
						if type(k)==type(1) and k not in [0,-1]:
							ocAppend=j[0].replace('goal_','')+': '+str(k)
						elif type(k)==type(0.1):
							ocAppend=j[0]+': '+str(k)
						elif k==True:
							ocAppend=j[0]
						elif j[0]=='statEffects' and k:
							ocAppend=', '.join(str(l['value'])+' '+' '.join(l['stat'].split('_')[1:]) for l in k)
						elif j[0]=='attributeEffects' and k:
							ocAppend=', '.join(l['attribute'].replace('_',' ') for l in k)
						try:
							if j[1] and 'statEffects' in j[1] and j[1]['statEffects']:
								ocAppend=', '.join([str(l['value'])+' '+' '.join(l['stat'].split('_')[1:]) for l in k['statEffects']])
						except:pass

						if dictAppend==ocAppend:
							notGarbageInfo.append(dictAppend)
						else:
							notGarbageInfo.append(dictAppend+' **__'+ocAppend+'__**')

							
					if 'damage_amount' in x and x['damage_amount'] and 'ticks' in x:
						#Damage chance is rolled against each model, until successes is equal to the max damaged entities
						#No overcasts change damage chance or max models damaged
						#Soul Quench is only spell here without ticks
						ticks=x['ticks']
						octicks=y['ticks']
						damageOutput=''
						if ticks==octicks:
							damageOutput+='ticks: '+str(ticks)
						else:
							damageOutput+='ticks: '+str(ticks)+' **__'+str(octicks)+'__**'
						if x['damage_amount']==y['damage_amount'] and ticks==octicks:
							if (x['max_damaged_entities'])==None:
								pass
							else:
								damageOutput+=', total damage: '+str(int(x['damage_amount']*x['max_damaged_entities']*ticks))+' ('+str(int(x['damage_amount']*ticks))+' vs single entities)'
						else:
							if (x['max_damaged_entities'])==None:
								pass
							else:
								damageOutput+=', total damage: '+str(int(x['damage_amount']*x['max_damaged_entities']*ticks))+' **__'+str(int(y['damage_amount']*y['max_damaged_entities']*octicks))+'__** ('+str(int(x['damage_amount']*ticks))+' **__'+str(int(y['damage_amount']*octicks))+'__** vs single entities)'
						notGarbageInfo.append(damageOutput)
					if 'heal_amount' in x and x['heal_amount']:
						ticks=x['ticks']
						octicks=y['ticks']
						if x['heal_amount']==y['heal_amount']:
							notGarbageInfo.append('Healing: '+str(round(x['heal_amount'],3)))
						else:
							notGarbageInfo.append('Healing: '+str(round(x['heal_amount'],3))+' **__'+str(round(y['heal_amount'],3))+'__**')
						if ticks==octicks:
							notGarbageInfo.append('ticks: '+str(ticks))
						else:
							notGarbageInfo.append('ticks: '+str(ticks)+' **__'+str(octicks)+'__**')
						if x['heal_amount']==y['heal_amount'] and ticks==octicks:
							notGarbageInfo.append('total healing: '+str(round(x['heal_amount']*ticks,3)))
						else:
							notGarbageInfo.append('total healing: '+str(round(x['heal_amount']*ticks,3))+' **__'+str(round(y['heal_amount']*octicks,3))+'__**')
					if notGarbageInfo:
						output+='\n'+(', '.join(sorted([i for i in notGarbageInfo if i!='']))).replace('__','abc123').replace('_',' ').replace('abc123','__').capitalize()
				spells[spellName]=output

				
			else:#Normal, has no overcast
				spelltype='_'.join(spell['type_key'].split('_')[2:]).replace('_',' ').capitalize()+', '
				output='**'+spell['name']+'**: '
				output+='*'+spell['tooltip'].strip()+'*\n'

				spell_sa=spell['special_ability']
				if spell_sa==None:continue
				basicInfo=[]
				for i in [("mp_cost",' gold'),("mana_cost",' mana'),("target_intercept_range",' meters'),('wind_up_time','s cast time'),("recharge_time",'s recharge')]:
					try:#Warp hunger spells don't have any basic info
						if i[0] in spell_sa.keys():
							if spell_sa[i[0]] in [0,-1]:#Passives
								continue
							basicInfo.append(str(spell_sa[i[0]])+i[1])
					except:
						pass
				for i in [('active_time','s duration'),('effect_range','m radius')]:
					try:
						if spell_sa[i[0]] not in [0,-1]:
							basicInfo.append(str(spell_sa[i[0]])+i[1])
					except:pass
				for i in [('num_effected_friendly_units',' max units')]:
					try:
						if spell_sa[i[0]] not in [1,0,-1]:
							basicInfo.append(str(spell_sa[i[0]])+i[1])
					except:pass

				output+=spelltype+', '.join(basicInfo)		
			
				dicts=['dominant_phase','phase', 'projectile', 'miscast_explosion_contact_phase_effect', 'spawned_unit', 'projectile_explosion_contact__effect', 
				'projectile_explosion', 'bombardment', 'projectile_contact_stat_effect', 'vortex', 'vortex_phase']
				for i in dicts:
					if i in spell.keys():
						x=spell[i]
					elif i in spell_sa.keys():
						x=spell_sa[i]
					else:continue
					if not x:continue
					notGarbageInfo=[]#No false booleans or uninteresting strings
					damageBase=x['damage'] if 'damage' in x else 0
					damageAP=x['damage_ap'] if 'damage_ap' in x else 0
					if damageBase:
						if damageAP:
							notGarbageInfo.append('Damage: '+str(damageBase+damageAP)+' ('+str(damageBase)+' base + '+str(damageAP)+' AP)')
						else:
							notGarbageInfo.append('Damage: '+str(damageBase)+' base')
					elif damageAP:
						notGarbageInfo.append('Damage: '+str(damageAP)+' AP')
					for j in x.items():
						if j[0] in ['damage','damage_ap', 'ticks']:continue
						if any(l in j[0] for l in ['expansion_speed','start_radius', 'change_max_angle','move_change_freq','is_magical','duration','elevation','calibration','minimum_range','frequency']):continue
						if any(l in j[0] for l in ['shots_per_volley','projectile_number']) and j[1]==1:continue
						if type(j[1])==type(1) and j[1] not in [0,-1]:
							notGarbageInfo.append(j[0].replace('goal_','')+': '+str(j[1]))
						elif type(j[1])==type(0.1):
							notGarbageInfo.append(j[0]+': '+str(round(j[1],3)))
						elif j[1]==True:
							notGarbageInfo.append(j[0])
						elif j[0]=='statEffects' and j[1]:
							for k in j[1]:
								notGarbageInfo.append(str(k['value'])+' '+' '.join(k['stat'].split('_')[1:]))
						elif j[0]=='attributeEffects' and j[1]:
							for k in j[1]:
								notGarbageInfo.append(k['attribute'].replace('_',' '))
						try:
							if j[1] and 'statEffects' in j[1] and j[1]['statEffects']:
								dictAppend=', '.join([str(l['value'])+' '+' '.join(l['stat'].split('_')[1:]) for l in j[1]['statEffects']])
						except:pass
					if 'damage_amount' in x and x['damage_amount']:
						#Damage chance is rolled against each model, until successes is equal to the max damaged entities
						ticks=x['ticks']
						if (x['max_damaged_entities'])==None:
							pass
						else:
							notGarbageInfo.append(('ticks: '+str(ticks)+', ')*int('ticks' in x)+'total damage: '+str(int(x['damage_amount']*(ticks if 'ticks' in x else 1)*x['max_damaged_entities']))+' ('+str(int(x['damage_amount']*(ticks if 'ticks' in x else 1)))+' vs single entities)')
					if 'heal_amount' in x and x['heal_amount']:
						notGarbageInfo.append('total healing: '+str(round(x['heal_amount']*x['ticks'],3)))
					if notGarbageInfo:
						output+='\n'+(', '.join(sorted(notGarbageInfo))).replace('_',' ').capitalize()

				spells[spellName]=output
		return spells