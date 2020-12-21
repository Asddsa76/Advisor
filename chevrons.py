import itertools

mult=[0.03, 0.06, 0.09, 0.12, 0.14, 0.17, 0.2, 0.23, 0.26]
fixed=[9, 18, 28, 40, 52, 65, 79, 94, 110]

async def chevrons(channel,target):
	target=int(target)
	if target>1000:
		await channel.send('Too much gold, just buy another unit')
		return
	a={'Spearmen':24, 'Rangers':27, 'Silver Helms':39}
	a=sorted(list(a.items()),key=lambda i:i[1])
	maxChevrons=[target//i[1] for i in a]
	iterables=[range(i+1) for i in maxChevrons]

	solutions=[]#(Spearmen, Rangers, Silver Helms, spent cash)
	for i in itertools.product(*iterables):
		cost=sum(i[j]*a[j][1] for j in range(len(i)))
		if cost<=target:
			solutions.append((i,cost))

	solutions=sorted(solutions,key=lambda x:-x[-1])[:5]
	output='('+', '.join(i[0] for i in a)+'), Gold remaining\n'
	output+='\n'.join(str(i[0])+', '+str(target-i[1]) for i in solutions)
	await channel.send(output)