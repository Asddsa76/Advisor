#A Total War Warhammer 2 info bot for Discord
#Data provided by https://twwstats.com/
#Project started on 25/1-2020

import asyncio
import discord
import random
from json import loads
from json import dumps
from re import finditer
from getAdvisorToken import * #Discord key is in a hidden file

#Commands meant for Probius
blacklist=['d', 're', 'rot']
def trim(x):
	for i in ",. -'`":
		x=x.replace(i,'')
	return x.lower()

print('Processing units...')
with open('Twisted and Twilight.json','rb') as g:
	units={}
	for unit in loads(g.read().decode('utf-8')):
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

print('Processing spells...')
with open('TTspells.json','rb') as h:
	spells={}
	for spell in loads(h.read().decode('utf-8')):
		if '_bound_' in spell['key']:continue#Don't process bound spells
		spelltype='_'.join(spell['type_key'].split('_')[2:]).replace('_',' ').capitalize()+', '
		output='**'+spell['name']+'**: '
		output+='*'+spell['tooltip'].strip()+'*\n'
		basicInfo=[]
		for i in [("sa_mana_cost",' mana'),("sa_target_intercept_range",' meters'),("sa_mp_cost",' gold'),("sa_recharge_time",'s recharge')]:
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
		'sa_projectile_explosion', 'sa_bombardment', 'sa_projectile_contact_stat_effect', 'overpower_option', 'sa_vortex', 'sa_vortex_phase']
		for i in dicts:
			if i in spell.keys():x=spell[i]
			else:continue
			if not x:continue
			notGarbageInfo=[]
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
				if j[0] in ['damage','damage_ap']:continue
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
			if 'damage_amount' in x and x['damage_amount']:
				notGarbageInfo.append('total expected damage: '+str(int(x['damage_amount']*(x['ticks'] if 'ticks' in x else 1)*x['damage_chance']*x['max_damaged_entities'])))
			if 'heal_amount' in x and x['heal_amount']:
				notGarbageInfo.append('total healing: '+str(x['heal_amount']*x['ticks']))
			if notGarbageInfo:
				output+='\n'+(', '.join(sorted(notGarbageInfo))).replace('_',' ').capitalize()

		spells[trim(spell['name'])]=output
print('Logging on Discord...')

async def aliases(unit,units,spells):
	unit=trim(unit)
	with open('aliases.txt','r') as f:
		for line in f.read().split('\n'):
			if unit in line.replace(' ','').split(':')[1].split(','):
				unit=line.split(':')[0]
				break
	output=[]
	for i in units.keys():
		if unit in i:
			output.append(i)
			continue
		try:
			if unit==''.join(j[0] for j in units[i]['name'].lower().split(' ')):
				output.append(i)
		except:pass
	for i in spells.keys():
		if unit in i:
			output.append(i)
			continue
		try:
			if unit==''.join(j[0] for j in spells[i].split('**')[1].lower().split(' ')):
				output.append(i)
		except Exception as e:
			pass
	
	if output:
		output.sort(key=lambda x:len(x))
		return output[:10]
	return 404



async def compactUnit(text):#Returns compact string of unit stats
	x=units[text]
	output='**'+x['name']+'** ('+x['category']+', '+str(x['multiplayer_cost'])+'g): '
	if x['unit_size']==1:
		output+=str(x["health"])+' hp, '
	else:
		output+=str(x["unit_size"])+' size, '+str(x["health"])+' hp ('+str(int(x["health"]/x["unit_size"]))+' each), '
	output+=str(x["armour"])+' armour, '+str(x["leadership"])+' leadership, '+str(x["speed"])+' speed'
	if x['missile_parry']!=0:
		output+=', '+str(x['missile_parry'])+'% missile parry'
	if x['resistances']:
		output+='\n*Resistances:* '+', '.join([str(x['resistances'][i])+'% '+i for i in x['resistances'].keys()])
	y=x['primary_melee_weapon']
	output+='\n*Melee:* '+str(x["melee_defence"])+' defence, '+str(x["melee_attack"])+' attack, '+str(y['damage'])+' ('+str(y['base_damage'])+' base + '+str(y['ap_damage'])+' AP) damage, '+str(x["charge_bonus"])+' charge bonus'
	for i in ['infantry','large']:
		if y['bonus_v_'+i]: output+=', '+str(y['bonus_v_'+i])+' bonus vs '+i
	if y['splash_attack_max_attacks']!=1:
		output+=', splash '+str(y['splash_attack_max_attacks'])+' '+(y['splash_attack_target_size'].replace('very_large','huge') if y['splash_attack_target_size'] else 'small')
	for i in [('ignition_amount','fire'),('is_magical','magical')]:
		if y[i[0]]:
			output+=', '+i[1]
	if x["primary_missile_weapon"]:#It's a ranged unit
		y=x['primary_missile_weapon']['projectile']
		output+='\n*Ranged:* '+str(y['range'])+'m, '+str(y['base_reload_time'])+'s reload, '+str(x['primary_missile_weapon']["damage"])+' ('+str(y["base_damage"])+' base + '+str(y["ap_damage"])+' AP) damage'
		for i in ['infantry','large']:
			if y['bonus_v_'+i]: output+=', '+str(y['bonus_v_'+i])+' bonus vs '+i
		if y['penetration_max_penetration']:
			output+=', penetration '+str(y['penetration_max_penetration'])+' '+y['penetration_entity_size_cap']
		for i in [('ignition_amount','fire'),('is_magical','magical')]:
			if y[i[0]]:
				output+=', '+i[1]
	if "abilities" in x.keys():
		output+='\n*Abilities:* '+', '.join(x['abilities'])
	if "attributes" in x.keys():
		output+='\n*Attributes:* '+', '.join(x['attributes'])
	if "spells" in x.keys():#It has spells or abilities
		output+='\n*Spells:* '+', '.join(x['spells'])
	return output

async def getUnitOrSpellString(unit):
	try:
		return (await compactUnit(unit))
	except Exception as e:
		return spells[unit]

#Voice state, sort alphabetically, P reaction
async def pick(member,textchannel):
	factions='Beastmen, Bretonnia, Dark Elves, Dwarfs, Empire, Greenskins, High Elves, Lizardmen, Norsca, Skaven, Tomb Kings, Vampire Coast, Vampire Counts, Warriors of Chaos, Wood Elves'
	factions=factions.split(', ')
	try:
		random.seed()
		message=await textchannel.send('\n'.join(sorted([(i.nick or i.name) +': '+random.choice(factions) for i in member.voice.channel.members])))
		await message.add_reaction('🇵')
	except:
		await textchannel.send("You're not in a voice channel!")

async def mainAdvisor(self,message,texts):
	channel=message.channel
	if message.channel.id==741762417976934460:#Message was intended for Probius
		if '/' in message.content or message.content in ['['+i for i in blacklist]+['['+i+']' for i in blacklist]:
			return
	loggingMessage=message.channel.guild.name+' '*(15-len(message.channel.guild.name))+message.channel.name+' '+' '*(17-len(message.channel.name))+str(message.author.name)+' '*(18-len(str(message.author.name)))+' '+message.content
	await client.get_channel(670838204265398292).send('`'+loggingMessage+'`')
	print(loggingMessage)
	pickAliases=['pick']
	for text in texts:
		if text[0]=="zerk's beard":
			await channel.send("**Zerk's Beard** (Facial hair, 250g): 1 size, 9999 hp, 99 armour, 99 leadership, 99 speed\n*Melee:* 99 defence, 99 attack, 198 (99 base + 99 AP) damage, 99 charge bonus, 99 bonus vs ladies")
			continue
		elif text[0]=='vote':
			await vote(message,text)
			continue
		elif text[0] in pickAliases:
			await pick(message.author,message.channel)
			continue
		elif text[0] in ['spell','spells']:#The spells of a unit
			unitSpells=units[(await aliases(text[1],units,{}))[0]]['spells']
			output=''
			for i in enumerate(unitSpells):
				output+=str(i[0]+1)+' - '+i[1]+'\n'
			sentMessage=await message.channel.send(output)
			for i in range(len(unitSpells)):
				try:#Try because message might be deleted before all emojis are sent
					await sentMessage.add_reaction(str(i+1)+'\N{combining enclosing keycap}')
				except:pass
			continue


		thingsToSend=await aliases(text[0],units,spells)
		if thingsToSend==404:
			continue
		output=await getUnitOrSpellString(thingsToSend[0])
		if len(thingsToSend)>1:
			output+='\n'*2
			for i in enumerate(thingsToSend):
				if i[0]==0:
					pass
				else:
					output+=str(i[0])+' - '+(await getUnitOrSpellString(i[1])).split('**')[1]+'\n'
		sentMessage=await message.channel.send(output)
		for i in range(len(thingsToSend)):
			if i==0:
				pass
			else:
				try:#Try because message might be deleted before all emojis are sent
					await sentMessage.add_reaction(str(i)+'\N{combining enclosing keycap}')
				except:pass

def findTexts(message):
	text=message.content.lower()
	leftBrackets=[1+m.start() for m in finditer('\[',text)]#Must escape brackets when using regex
	rightBrackets=[m.start() for m in finditer('\]',text)]
	texts=[text[leftBrackets[i]:rightBrackets[i]].split('/') for i in range(len(leftBrackets))]
	return texts

class MyClient(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_ready(self):
		print('Logged on as', self.user)
		print('Ready!')

	async def on_message_edit(self, before, after):
		#Don't respond to bots
		if after.author.bot:
			return
		if '[' in after.content and ']' in after.content:
			try:
				beforeTexts=findTexts(before)
			except:
				beforeTexts=[]
			newTexts=[i for i in findTexts(after) if i not in beforeTexts]
			if newTexts:#Nonempty lists have boolean value true
				await mainAdvisor(self,after,newTexts)

	async def on_message(self, message):
		#Don't respond to bots
		if message.author.bot:
			return
		if '[' in message.content and ']' in message.content:
			texts=findTexts(message)
			await mainAdvisor(self,message,texts)
		elif '[' in message.content:
			await mainAdvisor(self,message,[message.content.split('[')[1].lower().split('/')])

	async def on_raw_reaction_add(self,payload):
		member=client.get_user(payload.user_id)
		if member.bot:
			return
		message=await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
		if message.author.id==670832046389854239:#Message is from Advisor, and has a list
			if '🇵' in str(payload.emoji):
				member=message.channel.guild.get_member(payload.user_id)
				await pick(member,message.channel)
			elif '⃣' in str(payload.emoji) and '1 - ' in message.content:
				if message.reactions[[i.emoji for i in message.reactions].index(str(payload.emoji))].me:#Needs a reaction from Advisor
					number=str(payload.emoji)[0]
					name=trim(message.content.split(number+' - ')[1].split('\n')[0])
					await message.channel.send(await getUnitOrSpellString(name))
					await client.get_channel(670838204265398292).send(member.name+' reacted')
					await message.remove_reaction(payload.emoji,message.author)#Removes reaction
					#await message.delete()

async def vote(message,text):
	if len(text)==2:
		n=int(text[1])
		if n<1 or n>9:
			await message.channel.send('Out of range')
			return
		for i in range(1,n+1):
			await message.add_reaction(str(i)+'\N{combining enclosing keycap}')
	else:
		await message.add_reaction('\U0001f44d')
		await message.add_reaction('\U0001f44e')

intents = discord.Intents.default()  # All but the two privileged ones
intents.members = True  # Subscribe to the Members intent

asyncio.set_event_loop(asyncio.new_event_loop())
client = MyClient(command_prefix='!', intents=intents)
client.run(getAdvisorToken())