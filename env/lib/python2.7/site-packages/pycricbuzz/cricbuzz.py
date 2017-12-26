import requests
import json
import sys
from bs4 import BeautifulSoup

class Cricbuzz():
	url = "http://synd.cricbuzz.com/j2me/1.0/livematches.xml"
	def __init__(self):
		pass

	def getxml(self,url):
		try:
			r = requests.get(url)
		except requests.exceptions.RequestException as e: 
			print (e)
			sys.exit(1)
		soup = BeautifulSoup(r.text,"html.parser")
		return soup

	def matchinfo(self,match):
		d = {}
		d['id'] = match['id']
		d['srs'] = match['srs']
		d['mchdesc'] = match['mchdesc']
		d['mnum'] = match['mnum']
		d['type'] = match['type']
		d['mchstate'] = match.state['mchstate']
		d['status'] = match.state['status']
		return d

	def matches(self):
		xml = self.getxml(self.url)
		matches = xml.find_all('match')
		info = []
		
		for match in matches:
			info.append(self.matchinfo(match))
		return info

	def livescore(self,mid):
		xml = self.getxml(self.url)
		match = xml.find(id = mid)
		data = {}
		data['matchinfo'] = self.matchinfo(match)
		tdata = data
		try:
			curl = match['datapath'] + "commentary.xml"
			comm = self.getxml(curl)
			mscr = comm.find('mscr')
			batting = mscr.find('bttm')
			bowling = mscr.find('blgtm')
			batsman = mscr.find_all('btsmn')
			bowler= mscr.find_all('blrs')
			d = {}
			d['team'] = batting['sname']
			d['score'] = []
			d['batsman'] = []
			for player in batsman:
				d['batsman'].append({'name':player['sname'],'runs': player['r'],'balls':player['b'],'fours':player['frs'],'six':player['sxs']})
			binngs = batting.find_all('inngs')
			for inng in binngs:
				d['score'].append({'desc':inng['desc'], 'runs': inng['r'],'wickets':inng['wkts'],'overs':inng['ovrs']})
			data['batting'] = d
			d = {}
			d['team'] = bowling['sname']
			d['score'] = []
			d['bowler'] = []
			for player in bowler:
				d['bowler'].append({'name':player['sname'],'overs':player['ovrs'],'maidens':player['mdns'],'runs':player['r'],'wickets':player['wkts']})
			bwinngs = bowling.find_all('inngs')
			for inng in bwinngs:
				d['score'].append({'desc':inng['desc'], 'runs': inng['r'],'wickets':inng['wkts'],'overs':inng['ovrs']})
			data['bowling'] = d
			return data
		except:
			return tdata

	def commentary(self,mid):
		xml = self.getxml(self.url)
		match = xml.find(id = mid)
		data = {}
		data['matchinfo'] = self.matchinfo(match)
		tdata = data
		try:
			curl = match['datapath'] + "commentary.xml"
			comm = self.getxml(curl).find_all('c')
			d = []
			for c in comm:
				d.append(c.text)
			data['commentary'] = d
			return data 
		except:
			return tdata

	def scorecard(self,mid):
		xml = self.getxml(self.url)
		match = xml.find(id = mid)
		data = {}
		data['matchinfo'] = self.matchinfo(match)
		tdata = data
		try:
			surl = match['datapath'] + "scorecard.xml"
			scard = self.getxml(surl)
			scrs = scard.find('scrs')
			innings = scrs.find_all('inngs')
			squads = scard.find('squads')
			teams = squads.find_all('team')
			sq = []
			sqd = {}

			for team in teams:
				sqd['team'] = team['name']
				sqd['members'] = []
				members = team['mem'].split(", ")
				for mem in members:
					sqd['members'].append(mem)
				sq.append(sqd.copy())
			data['squad'] = sq	
			d = []
			card = {}
			for inng in innings:
				bat = inng.find('bttm')
				card['batteam'] = bat['sname']
				card['runs'] = inng['r']
				card['wickets'] = inng['wkts']
				card['overs'] = inng['ovrs']
				card['runrate'] = bat['rr']
				card['inngdesc'] = inng['desc']
				batplayers = bat.find_all('plyr')
				batsman = []
				bowlers = []
				for player in batplayers:
					status = player.find('status').text
					batsman.append({'name':player['sname'],'runs': player['r'],'balls':player['b'],'fours':player['frs'],'six':player['six'],'dismissal':status})
				card['batcard'] = batsman
				bowl = inng.find('bltm')
				card['bowlteam'] = bowl['sname']
				bowlplayers = bowl.find_all('plyr')
				for player in bowlplayers:
					bowlers.append({'name':player['sname'],'overs':player['ovrs'],'maidens':player['mdns'],'runs':player['roff'],'wickets':player['wkts']})
				card['bowlcard'] = bowlers
				d.append(card.copy())
			data['scorecard'] = d
			return data
		except:
			return tdata
		


