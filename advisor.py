#A Total War Warhammer 2 info bot for Discord
#Data provided by https://twwstats.com/
#Project started on 25/1-2020

from json import loads
from json import dumps
from re import finditer
from getAdvisorToken import * #Discord key is in a hidden file
import discord

def trim(x):
	for i in ",. -'`":
		x=x.replace(i,'')
	return x.lower()

with open('Skull_for_the_Skull_Throne_4-units.json','rb') as g:
	units={}
	for unit in loads(g.read().decode('utf-8')):
		for i in ['abilities','spells']:
			unit[i]=[j['name'] for j in unit[i]]
			if not unit[i]:
				del unit[i]
		unit['attributes']=[j['key'].replace('_',' ').capitalize().replace('Guerrilla','Vanguard') for j in unit['attributes']]
		if not unit['attributes']:
			del unit['attributes']
		unit['missile_parry']=unit["parry_chance"]
		resistances={}
		for i in ['flame','magic','physical','missile','all']:
			if unit['damage_mod_'+i]!=0:
				resistances[i]=unit['damage_mod_'+i]
		unit['resistances']=resistances
		units[trim(unit['name'])]=unit

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
	for i in spells.keys():
		if unit in i:
			output.append(i)
	
	if output:
		output.sort(key=lambda x:len(x))
		return output[:10]
	return 404

async def compactUnit(text):#Returns compact string of unit stats
	x=units[text]
	output='**'+x['name']+'** ('+x['category']+', '+str(x['multiplayer_cost'])+'g): '+str(x["unit_size"])+' size, '+str(x["health"])+' hp, '+str(x["armour"])+' armour, '+str(x["leadership"])+' leadership, '+str(x["speed"])+' speed'
	if x['missile_parry']!=0:
		output+=', '+str(x['missile_parry'])+'% missile parry'
	if x['resistances']:
		output+='\n*Resistances:* '+', '.join([str(x['resistances'][i])+'% '+i for i in x['resistances'].keys()])
	output+='\n*Melee:* '+str(x["melee_defence"])+' defence, '+str(x["melee_attack"])+' attack, '+str(x['primary_melee_weapon']['damage'])+' ('+str(x['primary_melee_weapon']['base_damage'])+' base + '+str(x['primary_melee_weapon']['ap_damage'])+' AP) damage, '+str(x["charge_bonus"])+' charge bonus'
	for i in ['infantry','large']:
		try:
			output+=', '+str(x['bonus_v_'+i])+' bonus vs '+i
		except:
			continue
	if x["primary_missile_weapon"]:#It's a ranged unit
		y=x['primary_missile_weapon']['projectile']
		output+='\n*Ranged:* '+str(y['range'])+'m, '+str(x['primary_missile_weapon']["damage"])+' ('+str(y["base_damage"])+' base + '+str(y["ap_damage"])+' AP) damage'
		for i in ['infantry','large']:
			try:
				output+=', '+str(y['missile_bonus_v_'+i])+' bonus vs '+i
			except:
				continue
	if "abilities" in x.keys():
		output+='\n*Abilities:* '+', '.join(x['abilities'])
	if "attributes" in x.keys():
		output+='\n*Attributes:* '+', '.join(x['attributes'])
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
		if member.id==670832046389854239:#Advisor did reaction
			return
		message=await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
		if message.author.id==670832046389854239 and '1 - ' in message.content:#Message is from Advisor, and has a list
			if '⃣' in str(payload.emoji):
				number=str(payload.emoji)[0]
				name=trim(message.content.split(number+' - ')[1].split('\n')[0])
				await message.channel.send(await getUnitOrSpellString(name))
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

client = MyClient()
client.run(getAdvisorToken())