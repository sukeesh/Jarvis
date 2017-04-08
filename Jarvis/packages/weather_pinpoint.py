from colorama import Fore
import mapps


def main(MEMORY):
    location = MEMORY.get_data('city')  # Will return None if no value
    if location is None:
        loc = str(location)
        city = mapps.getLocation()['city']
        print(Fore.RED + "It appears you are in " +
              city + " Is this correct? (y/n)" + Fore.RESET)

        try:
            i = raw_input()
        except:
            i = input()
        if i == 'n' or i == 'no':
            print("Enter Name of city: ")
            try:
                i = raw_input()
            except:
                i = input()
            city = i

        mapps.weather(str(city))

        MEMORY.update_data('city', city)
        MEMORY.save()
    else:
        loc = str(location)
        city = mapps.getLocation()['city']
        if city != loc:
            print(Fore.RED + "It appears you are in " + city +
                  ". But you set your location to " + loc + Fore.RESET)
            print(Fore.RED + "Do you want weather for " +
                  city + " instead? (y/n)" + Fore.RESET)
            try:
                i = raw_input()
            except:
                i = input()
            if i == 'y' or i == 'yes':
                try:
                    print(Fore.RED + "Would you like to set " + city +
                          " as your new location? (y/n)" + Fore.RESET)
                    try:
                        i = raw_input()
                    except:
                        i = input()
                    if i == 'y' or i == 'yes':
                        MEMORY.update_data('city', city)
                        MEMORY.save()

                    mapps.weather(city)
                except:
                    print(Fore.RED + "I couldn't locate you" + Fore.RESET)
            else:
                try:
                    mapps.weather(loc)
                except:
                    print(Fore.RED + "I couldn't locate you" + Fore.RESET)
        else:
            try:
                mapps.weather(loc)
            except:
                print(Fore.RED + "I couldn't locate you" + Fore.RESET)
