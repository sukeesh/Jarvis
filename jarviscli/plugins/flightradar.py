from plugin import plugin, require
from FlightRadar24.api import FlightRadar24API
flightapi = FlightRadar24API()

@require(network=True)
@plugin("flightradar")
def flightradar(jarvis, s):
    flightapi = FlightRadar24API()

    airports = flightapi.get_airports()
    airlines = flightapi.get_airlines()
    flights = flightapi.get_flights()

    option = int(input("What do you want to do:\n  1) Check Airline flights\n  2) Check Flight between Destinations\n 3) Track flight\nPlease chose between(1, 2, 3): "))

    if option == 1:
        get_input_method = int(input("How will you give the name of the airline:\n  1) By icao\n  2) By airline name\nPlease chose between(1, 2): "))
        if get_input_method == 1:
            airline_icao = input("What is the airlines icao: ")
            if airline_icao != "":
                airline_planes = flightapi.get_flights(airline = airline_icao.upper())
                airline_flights = []
                for plane in airline_planes:
                    if plane.altitude != 0:
                        airline_flights.append(plane)
                jarvis.say("{:^5} {:^10} {:^20} {:^22} {:^10}   {:^10} {:^10} ".format("ICAO", "Registration", "Origin Airport", "Destination Airport", "latitude", "longitude", "time"))
                for flight in airline_flights:
                    jarvis.say("{:^5} {:^10}   {:^20} {:^22} {:^10}   {:^10}  {:^10}".format(flight.airline_icao, flight.registration, flight.origin_airport_iata, flight.destination_airport_iata, flight.latitude, flight.longitude, flight.time))
            else:
                jarvis.say("Enter a ICAO")
        
        elif get_input_method == 2:
            airline_name = input("What is the airlines Name: ")
            if airline_name == "":
                jarvis.say("Enter a Airline name")
            run = False
            for airline in airlines:
                if airline["Name"].lower() == airline_name.lower():
                    airline_icao = airline["ICAO"]
                    run = True
                    break
            if run:
                airline_planes = flightapi.get_flights(airline = airline_icao)
                airline_flights = []
                for plane in airline_planes:
                    if plane.altitude != 0:
                        airline_flights.append(plane)
                jarvis.say("  {:^5}   {:^5} {:^10} {:^20} {:^22} {:^10}   {:^10} {:^10}".format("Name","ICAO", "Registration", "Origin Airport", "Destination Airport", "latitude", "longitude", "time"))
                for flight in airline_flights:
                    jarvis.say("{:^5}  {:^5} {:^10}   {:^20} {:^22} {:^10}   {:^10}  {:^10}".format(airline_name, flight.airline_icao, flight.registration, flight.origin_airport_iata, flight.destination_airport_iata, flight.latitude, flight.longitude, flight.time))
            else:
                jarvis.say("No airline found")
        else:
            jarvis.say("Enter a vaild option")

    elif option == 2:
        get_input_method = int(input("How will you give the name of the airports:\n  1) By iata\n  2) By airport name\nPlease chose between(1, 2): "))
        if get_input_method == 1:
            origin_airport_iata = input("What is the origin airport iata: ")
            destination_airport_iata = input("What is the destination airport iata: ")\
            
            if origin_airport_iata != destination_airport_iata:
                route_flights = []
                for plane in flights:
                    if (plane.origin_airport_iata == origin_airport_iata) and (plane.destination_airport_iata == destination_airport_iata):
                        route_flights.append(plane)
                jarvis.say("{:^5} {:^10} {:^20} {:^22} {:^10}   {:^10} {:^10}".format("ICAO", "Registration", "Origin Airport", "Destination Airport", "latitude", "longitude", "time"))
                for flight in route_flights:
                    jarvis.say("{:^5} {:^10}   {:^20} {:^22} {:^10}   {:^10}  {:^10}".format(flight.airline_icao, flight.registration, flight.origin_airport_iata, flight.destination_airport_iata, flight.latitude, flight.longitude, flight.time))
        
        
        elif get_input_method == 2:
            origin_airport_name = input("What is the origin airport name: ")
            destination_airport_name = input("What is the destination airport name: ")

            if origin_airport_name != destination_airport_name:
                run = False
                orun = False
                drun = False
                for airport in airports:
                    if airport["name"].lower() == origin_airport_name.lower():
                        origin_airport_iata = airport["iata"]
                        orun = True
                    elif airport["name"].lower() == destination_airport_name.lower():
                        destination_airport_iata = airport["iata"]
                        drun = True
                    if orun and drun:
                        run = True
                        break
                if run:
                    jarvis.say(destination_airport_iata, origin_airport_iata)

                    route_flights = []
                    for plane in flights:
                        if (plane.origin_airport_iata == origin_airport_iata) and (plane.destination_airport_iata == destination_airport_iata):
                            route_flights.append(plane)
                    jarvis.say("{:^5} {:^10} {:^20} {:^22} {:^10}   {:^10} {:^10}".format("ICAO", "Registration", "Origin Airport", "Destination Airport", "latitude", "longitude", "time"))
                    for flight in route_flights:
                        jarvis.say("{:^5} {:^10}   {:^20} {:^22} {:^10}   {:^10}  {:^10}".format(flight.airline_icao, flight.registration, flight.origin_airport_iata, flight.destination_airport_iata, flight.latitude, flight.longitude, flight.time))
                else:
                    if not orun and not drun:
                        jarvis.say("Neither origin and destination airports were found")
                    elif not orun:
                        jarvis.say("The origin airport wasn't found")
                    elif not drun:
                        jarvis.say("The destination airport wasn't found")
        else:
            jarvis.say("Enter a vaild option")

    elif option == 3:
        flight_resgitration = input("What is the airplane resgistration: ")
        
        for flight in flights:
            if flight.registration == flight_resgitration:
                jarvis.say("{:^5} {:^10} {:^20} {:^22} {:^10}   {:^10} {:^10}".format("ICAO", "Registration", "Origin Airport", "Destination Airport", "latitude", "longitude", "time"))
                jarvis.say("{:^5} {:^10}   {:^20} {:^22} {:^10}   {:^10}  {:^10}".format(flight.airline_icao, flight.registration, flight.origin_airport_iata, flight.destination_airport_iata, flight.latitude, flight.longitude, flight.time))
                break

    else:
        jarvis.say("Enter a vaild option")
