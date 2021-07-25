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
			if '_upgraded' in spell['key'] or 'Master Rune' in spell['name']:#Overcast
				ocJSON[spell['key']]=spell
			else:
				spellJSON.append(spell)

		for spell in spellJSON:
			if spell['has_overcast']==True:
				oc=ocJSON[spell['overpower_option']['key']]
				output='**'+spell['name']+'**: '
				output+='*'+spell['tooltip'].strip()+'*\n'
				basicInfo=[]
				for i in [("sa_mp_cost",' gold'),("sa_mana_cost",' mana'),("sa_target_intercept_range",' meters'),('sa_wind_up_time','s cast time'),("sa_recharge_time",'s recharge')]:
					try:#Warp hunger spells don't have any basic info
						if i[0] in spell.keys():
							if spell[i[0]] in [0,-1]:#Passives
								continue
							if oc[i[0]]==spell[i[0]]:
								basicInfo.append(str(spell[i[0]])+i[1])
							else:
								basicInfo.append(str(spell[i[0]])+' **__'+str(oc[i[0]])+'__**'+i[1])
					except:
						pass
				for i in [('sa_active_time','s duration'),('sa_effect_range','m radius')]:
					try:
						if spell[i[0]] not in [0,-1]:
							if oc[i[0]]==spell[i[0]]:
								basicInfo.append(str(spell[i[0]])+i[1])
							else:
								basicInfo.append(str(spell[i[0]])+' **__'+str(oc[i[0]])+'__**'+i[1])
						elif oc[i[0]] not in [0,-1]:
							basicInfo.append('**__'+str(oc[i[0]])+i[1]+'__**')
					except:pass

				for i in [('sa_num_effected_friendly_units',' max units')]:
					try:
						if spell[i[0]] not in [1,0,-1]:
							if oc[i[0]]==spell[i[0]]:
								basicInfo.append(str(spell[i[0]])+i[1])
							else:
								basicInfo.append(str(spell[i[0]])+' **__'+str(oc[i[0]])+'__**'+i[1])
					except:pass

				spelltype='_'.join(spell['type_key'].split('_')[2:]).replace('_',' ').capitalize()+', '
				output+=spelltype+', '.join(basicInfo)
			
				dicts=['sa_phase', 'sa_projectile', 'sa_miscast_explosion_contact_phase_effect', 'sa_spawned_unit', 'sa_projectile_explosion_contact__effect', 
				'sa_projectile_explosion', 'sa_bombardment', 'sa_projectile_contact_stat_effect', 'sa_vortex', 'sa_vortex_phase']
				for i in dicts:
					if i in spell.keys():x=spell[i]
					else:continue
					if not x:continue
					y=oc[i]
					'''
					print('\noc: '+str(oc))
					print('i: '+str(i))
					print('x: '+str(x))
					print('y: '+str(y))'''
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
						if j[0] in ['damage','damage_ap','ticks','heal_amount']:continue
						if any(l in j[0] for l in ['expansion_speed','start_radius', 'change_max_angle','move_change_freq','is_magical','duration','elevation','calibration','minimum_range','frequency']):continue
						if any(l in j[0] for l in ['shots_per_volley','projectile_number']) and j[1]==1:continue
						k=y[j[0]]
						if 0:#j==k:
							if type(j[1])==type(1) and j[1] not in [0,-1]:
								notGarbageInfo.append(j[0].replace('goal_','')+': '+str(j[1]))
							elif type(j[1])==type(0.1):
								notGarbageInfo.append(j[0]+': '+str(j[1]))
							elif j[1]==True:
								notGarbageInfo.append(j[0])
							elif j[0]=='statEffects' and j[1]:
								for k in j[1]:
									notGarbageInfo.append(str(k['value'])+' '+' '.join(k['stat'].split('_')[1:]))
							elif j[0]=='attributeEffects' and j[1]:
								for k in j[1]:
									notGarbageInfo.append(k['attribute'].replace('_',' '))
						else:
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

							if dictAppend==ocAppend:
								notGarbageInfo.append(dictAppend)
							else:
								notGarbageInfo.append(dictAppend+' **__'+ocAppend+'__**')

							
					if 'damage_amount' in x and x['damage_amount'] and 'ticks' in x:
						#Damage chance is rolled against each model, until successes is equal to the max damaged entities
						#No overcasts change damage chance or max models damaged
						#Soul Quench is only spell here without ticks
						ticks=int(x['duration']/x['hp_change_frequency'])
						octicks=int(y['duration']/y['hp_change_frequency'])
						damageOutput=''
						if ticks==octicks:
							damageOutput+='ticks: '+str(ticks)
						else:
							damageOutput+='ticks: '+str(ticks)+' **__'+str(octicks)+'__**'
						if x['damage_amount']==y['damage_amount'] and ticks==octicks:
							damageOutput+=', total damage: '+str(int(x['damage_amount']*x['max_damaged_entities']*ticks))+' ('+str(int(x['damage_amount']*x['damage_chance']*ticks))+' vs single entities)'
						else:
							damageOutput+=', total damage: '+str(int(x['damage_amount']*x['max_damaged_entities']*ticks))+' **__'+str(int(y['damage_amount']*y['max_damaged_entities']*octicks))+'__** ('+str(int(x['damage_amount']*x['damage_chance']*ticks))+' **__'+str(int(y['damage_amount']*y['damage_chance']*octicks))+'__** vs single entities)'
						notGarbageInfo.append(damageOutput)
					if 'heal_amount' in x and x['heal_amount']:
						ticks=int(x['duration']/x['hp_change_frequency'])
						octicks=int(y['duration']/y['hp_change_frequency'])
						if x['heal_amount']==y['heal_amount']:
							notGarbageInfo.append('Healing: '+str(x['heal_amount']))
						else:
							notGarbageInfo.append('Healing: '+str(x['heal_amount'])+' **__'+str(y['heal_amount'])+'__**')
						if ticks==octicks:
							notGarbageInfo.append('ticks: '+str(ticks))
						else:
							notGarbageInfo.append('ticks: '+str(ticks)+' **__'+str(octicks)+'__**')
						if x['heal_amount']==y['heal_amount'] and ticks==octicks:
							notGarbageInfo.append('total healing: '+str(int(x['heal_amount']*ticks)))
						else:
							notGarbageInfo.append('total healing: '+str(int(x['heal_amount']*ticks))+' **__'+str(int(y['heal_amount']*octicks))+'__**')
					if notGarbageInfo:
						output+='\n'+(', '.join(sorted([i for i in notGarbageInfo if i!='']))).replace('__','abc123').replace('_',' ').replace('abc123','__').capitalize()
				spells[trim(spell['name'])]=output

				
			else:#Normal, has no overcast
				spelltype='_'.join(spell['type_key'].split('_')[2:]).replace('_',' ').capitalize()+', '
				output='**'+spell['name']+'**: '
				output+='*'+spell['tooltip'].strip()+'*\n'
				basicInfo=[]
				for i in [("sa_mp_cost",' gold'),("sa_mana_cost",' mana'),("sa_target_intercept_range",' meters'),('sa_wind_up_time','s cast time'),("sa_recharge_time",'s recharge')]:
					try:#Warp hunger spells don't have any basic info
						if i[0] in spell.keys():
							if spell[i[0]] in [0,-1]:#Passives
								continue
							basicInfo.append(str(spell[i[0]])+i[1])
					except:
						pass
				for i in [('sa_active_time','s duration'),('sa_effect_range','m radius')]:
					try:
						if spell[i[0]] not in [0,-1]:
							basicInfo.append(str(spell[i[0]])+i[1])
					except:pass
				for i in [('sa_num_effected_friendly_units',' max units')]:
					try:
						if spell[i[0]] not in [1,0,-1]:
							basicInfo.append(str(spell[i[0]])+i[1])
					except:pass

				output+=spelltype+', '.join(basicInfo)		
			
				dicts=['sa_phase', 'sa_projectile', 'sa_miscast_explosion_contact_phase_effect', 'sa_spawned_unit', 'sa_projectile_explosion_contact__effect', 
				'sa_projectile_explosion', 'sa_bombardment', 'sa_projectile_contact_stat_effect', 'sa_vortex', 'sa_vortex_phase']
				for i in dicts:
					if i in spell.keys():x=spell[i]
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
						if j[0] in ['damage','damage_ap','ticks']:continue
						if any(l in j[0] for l in ['expansion_speed','start_radius', 'change_max_angle','move_change_freq','is_magical','duration','elevation','calibration','minimum_range','frequency']):continue
						if any(l in j[0] for l in ['shots_per_volley','projectile_number']) and j[1]==1:continue
						if type(j[1])==type(1) and j[1] not in [0,-1]:
							notGarbageInfo.append(j[0].replace('goal_','')+': '+str(j[1]))
						elif type(j[1])==type(0.1):
							notGarbageInfo.append(j[0]+': '+str(j[1]))
						elif j[1]==True:
							notGarbageInfo.append(j[0])
						elif j[0]=='statEffects' and j[1]:
							for k in j[1]:
								notGarbageInfo.append(str(k['value'])+' '+' '.join(k['stat'].split('_')[1:]))
						elif j[0]=='attributeEffects' and j[1]:
							for k in j[1]:
								notGarbageInfo.append(k['attribute'].replace('_',' '))
					if 'damage_amount' in x and x['damage_amount']:
						#Damage chance is rolled against each model, until successes is equal to the max damaged entities
						ticks=int(x['duration']/x['hp_change_frequency'])
						notGarbageInfo.append(('ticks: '+str(ticks)+', ')*int('ticks' in x)+'total damage: '+str(int(x['damage_amount']*(ticks if 'ticks' in x else 1)*x['max_damaged_entities']))+' ('+str(int(x['damage_amount']*(ticks if 'ticks' in x else 1)*x['damage_chance']))+' vs single entities)')
					if 'heal_amount' in x and x['heal_amount']:
						notGarbageInfo.append('total healing: '+str(int(x['heal_amount']*x['duration']/x['hp_change_frequency'])))
					if notGarbageInfo:
						output+='\n'+(', '.join(sorted(notGarbageInfo))).replace('_',' ').capitalize()

				spells[trim(spell['name'])]=output
		return spells