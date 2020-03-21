#A Total War Warhammer 2 info bot for Discord
#Data provided by https://twwstats.com/
#Project started on 25/1-2020

from json import loads
from json import dumps
from re import finditer
from getAdvisorToken import * #Discord key is in a hidden file
from aliases import * #Alternate names
import discord

def trim(x):
	for i in ",. -'`":
		x=x.replace(i,'')
	return x.lower()

def jprint(x): #Prints the JSON in pretty print. Not called anywhere
	print(dumps(units[trim(x)],indent=4,sort_keys=False))

with open('oldUnits.json','rb') as g:
	oldUnits={}
	for oldUnit in loads(g.read().decode('utf-8'))['units']:
		oldUnits[trim(oldUnit['name'])]=oldUnit
	with open('units.json','rb') as f:
		deleteValues=[0,'null','',None,[]]
		deleteKeys=['factions','ground_stat_effect_group','key','tww_version','unit_card','radius',"shots_per_volley","reload_time","projectile_number"]
		units={}
		for unit in loads(f.read().decode('utf-8'))['units']:
			toDelete=[]
			for item in unit.items():
				if (item[1] in deleteValues and item[0]!='armour') or item[0] in deleteKeys:
					toDelete.append(item[0])
			for key in toDelete:
				del unit[key]
				pass
			oldUnit=oldUnits[trim(unit['name'])]
			for i in ['abilities','spells']:
				unit[i]=[j['name'] for j in oldUnit[i]]
				if not unit[i]:
					del unit[i]
			units[trim(unit['name'])]=unit
del oldUnits

with open('spells.json','rb') as h:
	spells={}
	for spell in loads(h.read().decode('utf-8'))['data']['tww']['abilities']:
		info=spell['unit_special_ability']
		output='**'+spell['name']+'**: '
		basicInfo=[]
		for i in [("mana_cost",'WoM'),("recharge_time",'s'),("target_intercept_range",'m'),("mp_cost",'g')]:
			try:#Warp hunger spells don't have any basic info
				if i[0] in info.keys():
					if info[i[0]] in [0,-1]:#Passives
						continue
					basicInfo.append(str(info[i[0]])+i[1])
			except:
				pass
		output+=', '.join(basicInfo)
		output+='\n*'+spell['tooltip'].strip()+'*'
		
		spells[trim(spell['name'])]=output

async def compactUnit(text):#Returns compact string of unit stats
	x=units[text]
	output='**'+x['name']+'** ('+x['category']+', '+str(x['multiplayer_cost'])+'g): '+str(x["unit_size"])+' size, '+str(x["health"])+' hp, '+str(x["armour"])+' armour, '+str(x["leadership"])+' leadership, '+str(x["speed"])+' speed'
	output+='\n*Melee:* '+str(x["melee_defence"])+' defence, '+str(x["melee_attack"])+' attack, '+str(x['damage'])+' ('+str(x['base_damage'])+' base + '+str(x['ap_damage'])+' AP) damage, '+str(x["charge_bonus"])+' charge bonus'
	for i in ['infantry','large']:
		try:
			output+=', '+str(x['bonus_v_'+i])+' bonus vs '+i
		except:
			continue
	if "missile_damage" in x.keys():#It's a ranged unit
		output+='\n*Ranged:* '+str(x['range'])+'m, '+str(x["missile_damage"])+' ('+str(x["missile_base_damage"])+' base + '+str(x["missile_ap_damage"])+' AP) damage'
		for i in ['infantry','large']:
			try:
				output+=', '+str(x['missile_bonus_v_'+i])+' bonus vs '+i
			except:
				continue
	if "abilities" in x.keys():
		output+='\n*Abilities:* '+', '.join(x['abilities'])
	if "spells" in x.keys():#It has spells or abilities
		output+='\n*Spells:* '+', '.join(x['spells'])
	return output

async def getUnitOrSpellString(unit):
	try:
		return spells[unit]
	except:
		return (await compactUnit(unit))


async def mainAdvisor(self,message,texts):
	channel=message.channel
	loggingMessage=message.channel.guild.name+' '*(15-len(message.channel.guild.name))+message.channel.name+' '+' '*(17-len(message.channel.name))+str(message.author.name)+' '*(18-len(str(message.author.name)))+' '+message.content
	await client.get_channel(670838204265398292).send('`'+loggingMessage+'`')
	print(loggingMessage)
	for text in texts:
		if text[0]=="zerk's beard":
			await channel.send("**Zerk's Beard** (Facial hair, 250g): 1 size, 9999 hp, 99 armour, 99 leadership, 99 speed\n*Melee:* 99 defence, 99 attack, 198 (99 base + 99 AP) damage, 99 charge bonus, 99 bonus vs ladies")
			continue
		elif text[0]=='vote':
			await vote(message,text)
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
					output+=str(i[0])+' - '+i[1]+'\n'
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
		if member.id==670832046389854239:#Advisor did reaction
			return
		message=await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
		if message.author.id==670832046389854239 and '1 - ' in message.content:#Message is from Advisor, and has a list
			if '⃣' in str(payload.emoji):
				number=str(payload.emoji)[0]
				name=message.content.split(number+' - ')[1].split('\n')[0]
				await message.channel.send(await getUnitOrSpellString(name))
				await message.delete()

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

client = MyClient()
client.run(getAdvisorToken())