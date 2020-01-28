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

def jprint(x): #Prints the JSON in pretty print. Not called anywhere
	print(dumps(units[trim(x)],indent=4,sort_keys=False))

with open('units.json','rb') as f:
	deleteValues=[0,'null','',None,[]]
	deleteKeys=['factions','ground_stat_effect_group','key','tww_version','unit_card','radius',"shots_per_volley","reload_time","projectile_number"]
	units={}
	for unit in loads(f.read())['units']:
		toDelete=[]
		for item in unit.items():
			if item[1] in deleteValues or item[0] in deleteKeys:
				toDelete.append(item[0])
		for key in toDelete:
			del unit[key]
			pass
		units[trim(unit['name'])]=unit

async def aliases(unit):
	unit=trim(unit)
	if unit in ['hoemaster','hoemasters','hoemastersofswordeth']:
		return 'swordmastersofhoeth'
	if unit in ['lsg']:
		return 'lothernseaguard'
	if unit in ['hge']:
		return 'harganethexecutioners'
	
	for i in units.keys():#Exact match first to not return RoR versions instead of default units, etc.
		if unit==i:
			return i
	for i in units.keys():
		if unit in i:
			return i
	return 404

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
	return output

async def mainAdvisor(self,message,texts):
	channel=message.channel
	loggingMessage=message.channel.guild.name+' '*(15-len(message.channel.guild.name))+message.channel.name+' '+' '*(17-len(message.channel.name))+str(message.author)+' '*(18-len(str(message.author)))+' '+message.content
	await client.get_channel(670838204265398292).send('`'+loggingMessage+'`')
	for text in texts:
		text=await aliases(text[0])
		if text==404:
			continue
		await channel.send(await compactUnit(text))

def findTexts(message):
	text=message.content.lower()
	leftBrackets=[1+m.start() for m in finditer('\[',text)]#Must escape brackets when using regex
	rightBrackets=[m.start() for m in finditer('\]',text)]
	texts=[text[leftBrackets[i]:rightBrackets[i]].split('/') for i in range(len(leftBrackets))]
	return texts

class MyClient(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.units={}

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

client = MyClient()
client.run(getAdvisorToken())