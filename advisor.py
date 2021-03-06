#A Total War Warhammer 2 info bot for Discord
#Data provided by https://twwstats.com/
#Project started on 25/1-2020

import asyncio
import discord
import random
from json import loads
from re import finditer
from getAdvisorToken import * #Discord key is in a hidden file
from chevrons import *
from units import *
from spells import *

#Commands meant for Probius
blacklist=['d', 're', 'rot', 'b','all']
def trim(x):
	for i in ",. -'`":
		x=x.replace(i,'')
	return x.lower()

async def mainAdvisor(self,message,texts):
	channel=message.channel
	if message.channel.id==741762417976934460:#Message was intended for Probius
		if message.content in ['['+i for i in blacklist]+['['+i+']' for i in blacklist]:
			return
	loggingMessage=message.channel.guild.name+' '*(15-len(message.channel.guild.name))+message.channel.name+' '+' '*(25-len(message.channel.name))+str(message.author.name)+' '*(18-len(str(message.author.name)))+' '+message.content
	await client.get_channel(670838204265398292).send('`'+loggingMessage+'`')
	print(loggingMessage)
	for text in texts:
		if text[0]=="zerk's beard":
			await channel.send("**Zerk's Beard** (Facial hair, 250g): 1 size, 9999 hp, 99 armour, 99 leadership, 99 speed\n*Melee:* 99 defence, 99 attack, 198 (99 base + 99 AP) damage, 99 charge bonus, 99 bonus vs ladies")
			continue
		elif text[0] in ['armor','armor']:
			await message.channel.send('https://cdn.discordapp.com/attachments/787967571135037451/794952578914844672/unknown.png')
			continue
		elif text[0] in ['chevron','chevrons','c','ch']:
			await chevrons(message.channel,text[1])
			continue
		elif text[0] in ['pickmap','map','maps','pickmaps']:
			await pickMaps(message.channel,self)
			continue
		elif text[0]=='vote':
			await vote(message,text)
			continue
		elif text[0] in ['pick']:
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

print('Processing units...')
units=units('Twisted and Twilight.json')
print('Processing spells...')
spells=spells('TTspells.json')
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
			elif 'the'==i[:3] and unit==''.join([j[0] for j in units[i].split('**')[1].lower().split(' ')][1:]):
				output.append(i)
		except:pass
	for i in spells.keys():
		if unit in i:
			output.append(i)
			continue
		try:
			if unit==''.join(j[0] for j in spells[i].split('**')[1].lower().split(' ')):
				output.append(i)
			elif 'the'==i[:3] and unit==''.join([j[0] for j in spells[i].split('**')[1].lower().split(' ')][1:]):
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
		try:#Grenade outriders don't have penetration in the json
			if y['penetration_max_penetration'] and y['penetration_entity_size_cap']!='very_small':#Only spider hatchlings are very small
				output+=', penetration '+str(y['penetration_max_penetration'])+' '+y['penetration_entity_size_cap'].replace('_',' ')
		except:pass
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

async def pick(member,textchannel):
	factions='Beastmen, Bretonnia, Dark Elves, Dwarfs, Empire, Greenskins, High Elves, Lizardmen, Norsca, Skaven, Tomb Kings, Vampire Coast, Vampire Counts, Warriors of Chaos, Wood Elves'
	factions=factions.split(', ')
	try:
		random.seed()
		message=await textchannel.send('\n'.join(sorted([(i.nick or i.name) +': '+random.choice(factions) for i in member.voice.channel.members])))
		await message.add_reaction('🇵')
	except:
		await textchannel.send("You're not in a voice channel!")

async def pickMaps(channel,client):
	maps=(await client.get_channel(714829266822496256).fetch_message(789818744569856010)).content.split('\n')
	random.seed()
	threeMaps=random.sample(maps,3)
	await channel.send('\n'.join(str(i+1)+'. '+threeMaps[i] for i in range(3)))



def findTexts(message):
	allTexts=[]
	wholeText=message.content.lower()
	for text in wholeText.split('\n'):
		if '>' in text and '<' not in text:#This line is a quote
			continue
		leftBrackets=[1+m.start() for m in finditer('\[',text)]#Must escape brackets when using regex
		rightBrackets=[m.start() for m in finditer('\]',text)]
		texts=[text[leftBrackets[i]:rightBrackets[i]].split('/') for i in range(len(rightBrackets))]
		if len(leftBrackets)>len(rightBrackets):#One extra unclosed at end
			texts.append(text[leftBrackets[-1]:].split('/'))
		allTexts+=texts
	return allTexts

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
		if '[' in after.content:
			try:
				beforeTexts=findTexts(before)
			except:
				beforeTexts=[]
			newTexts=[i for i in findTexts(after) if i not in beforeTexts]
			if newTexts:
				await mainAdvisor(self,after,newTexts)

	async def on_message(self, message):
		#Don't respond to bots
		if message.author.bot:
			return
		if '[' in message.content:
			await mainAdvisor(self,message,findTexts(message))

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
					if message.channel.guild.id==329723018958077963:
						await message.remove_reaction(payload.emoji,message.author)#Removes reaction

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