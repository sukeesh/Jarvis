from xmlrpc.client import getparser
from plugin import plugin, require

from colorama import Fore
import requests
#from ryanair import Ryanair
from FlightRadar24.api import FlightRadar24API

@require(network=True)
@plugin('flights')
class Flights():
    def __call__ (self,jarvis,s):
        self.flights(jarvis,s)
    def flights(self,jarvis, s):
        fr_api = FlightRadar24API()
        jarvis.say("Welcome to Flight module."+ "\n")
        self.newRadarApp(jarvis,s)


    def newRadarApp(self,jarvis, s):
        url='https://app.goflightlabs.com/flights?access_key='
        api_key= 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0IiwianRpIjoiZDFhOGFjNjgwZWZkY2Q2MGY5MzhhZTk1MTI3NjM0NDVjNjMzMjVkNGVlNWI1M2EzZmRjNzZmNWM3OTNmZjU4MTFmNTBlM2NkMzRlN2FiMTYiLCJpYXQiOjE2NjYzNDExNjksIm5iZiI6MTY2NjM0MTE2OSwiZXhwIjoxNjk3ODc3MTY5LCJzdWIiOiIxNTY5NCIsInNjb3BlcyI6W119.NRSmV9ZhyZE86sFcb0LZLJHv8V14QsPgJ9Lm_RJH46h3-aDnDzBSUezHy1isx7vaU2V5WuZdxhW_Ieb5bJlSpg'
        query = self.getParams(jarvis)
        if query == 'q':
            return-1
        jarvis.say(query)
        jarvis.say('Getting results ...')
        try:
            req = requests.get(url+ api_key+query)
        except:
            jarvis.say('Something went wrong, please try again')
        try:
            flight = req.json()
        except:
            jarvis.say('Something went wrong during parsing JSON')
            return -1
        jarvis.say('Filter results, select how many results to display')
        
        display= jarvis.input()
        print(display)
        while display.isnumeric()==False:
            jarvis.say('Please input number:')
            display= input()
        self.print_results(jarvis, flight,display)


    def getParams(self,jarvis):
        jarvis.say('select params: 1-status 2-dep 3-arr 4-airline 5-flight number 6-flight code q to quit')
        user=jarvis.input()
        userState=['1','2','3','4','5','6','q']
        query=''
        while user not in userState:
            jarvis.say('insert valid option')
            user=jarvis.input()
        if '1' in user:
            status_state=['scheduled', 'active', 'landed', 'cancelled', 'incident', 'diverted']
            jarvis.say('Enter flight status: scheduled, active, landed, cancelled, incident, diverted')
            status=jarvis.input()
            while status not in status_state:
                jarvis.say('Please input valid state')
                status=jarvis.input()

            query= query+'&flight_status='+status
        elif '2' in user:
            jarvis.say('Enter departure airport iata code: LHR')
            dep=jarvis.input()
            query= query+'&dep_iata='+dep.upper()
        elif '3' in user:
            jarvis.say('Enter arrival airport iata code: LHR')
            arr=jarvis.input()
            query= query+'&arr_iata='+arr.upper()
        elif '4' in user:
            jarvis.say('Enter airline name: Ryanair')
            dep=jarvis.input()
            query= query+'&airline_name='+dep
        elif '5' in user:
            jarvis.say('Enter flight number:')
            num=jarvis.input()
            query= query+'&flight_number='+num.upper()
        elif '6' in user:
            jarvis.say('Enter flight code:')
            dep=jarvis.input()
            query= query+'&flight_iata='+dep.upper()
        elif user == 'q':
            return 'q'
        return query
        
    def check_value(self,value):
        if value == None:
            
            value='None'
            return 'None'
        else:
            return value

    def print_live_flights(self,jarvis,flight):
        jarvis.say('latitude: ' + str(flight['live']['latitude']))
        jarvis.say('longitude: ' +str(flight['live']['longitude']))
        jarvis.say('altitude: ' +str(flight['live']['altitude']))
        jarvis.say('direction: ' +str(flight['live']['direction']))
        jarvis.say('speed horizontal: ' +str(flight['live']['speed_horizontal']))


    def print_results(self,jarvis, flights, number_of_prints):
        #print(flights)
        if 'success' in flights and flights['success'] == False:
            jarvis.say('No data found, please try again')
            return -1
        i=0
        while i<int(number_of_prints):
            text = Fore.RED + \
                'FLIGHT' + Fore.RESET
            jarvis.say(text)
            
            if 'departure' not in flights:
                jarvis.say('No data found, please try again')
                return -1
            dep_airport1=flights[i]['departure']['terminal']
            dep_airport=self.check_value(dep_airport1) 
            dep_terminal1=flights[i]['departure']['terminal']
            dep_terminal=self.check_value(dep_terminal1)
            dep_country1= flights[i]['departure']['timezone']
            dep_country= self.check_value(dep_country1)
            dep_gate1=flights[i]['departure']['gate']
            dep_gate=self.check_value(dep_gate1)
            dep_scheduled1=flights[i]['departure']['scheduled']
            dep_scheduled=self.check_value(dep_scheduled1)

            arr_airport1=flights[i]['arrival']['airport']
            arr_country1= flights[i]['arrival']['timezone']
            arr_terminal1=flights[i]['arrival']['terminal']
            arr_gate1=flights[i]['arrival']['gate']
            arr_airport=self.check_value(arr_airport1)
            arr_country=self.check_value(arr_country1)
            arr_terminal=self.check_value(arr_terminal1)
            arr_gate=self.check_value(arr_gate1)
            arr_delay1=flights[i]['arrival']['scheduled']
            arr_scheduled=self.check_value(arr_delay1)

            jarvis.say('Flight status: ' + flights[i]['flight_status'])

            text = Fore.BLUE + \
                'DEPARTURE' + Fore.RESET
            jarvis.say(text)
            jarvis.say('Departure airport: ' +dep_airport)
            jarvis.say('Departure country: ' + dep_country)
            
            #jarvis.say(flights[0]['departure']['airport'])
            jarvis.say('Departure terminal: ' + dep_terminal)
            jarvis.say('Departure gate: ' + dep_gate)
            jarvis.say('Departure scheduled: '+dep_scheduled) 
            #jarvis.say(str(dep_delay))
            
            text1 = Fore.BLUE + \
                'ARRIVAL' + Fore.RESET
            jarvis.say(text1)
            
        
            jarvis.say('Arrival airport: ' + arr_airport)
            jarvis.say('Arrival country: ' + arr_country)
            jarvis.say('Arrival terminal: ' + arr_terminal)
            jarvis.say('Arrival gate: ' + arr_gate)
            jarvis.say('Arrival scheduled: ') 
            #jarvis.say(flights[0]['arrival']['delay'])

            if flights[i]['live']!=None:
                jarvis.say('live:')
                print( flights[i]['live'])
                self.print_live_flights(jarvis,flights[i])
            i=i+1
