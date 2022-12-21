import webbrowser
from colorama import Fore
from plugin import plugin


@plugin("goodreads")
def goodreads(jarvis,s):
  jarvis.say("		Type 1 to see the most read books this week", Fore.BLUE)
  jarvis.say("		Type 2 to search for a book by title or ISBN", Fore.BLUE)
  jarvis.say("		Type 3 to search for an author", Fore.BLUE)
  jarvis.say("		Type 4 to see suggestions by genre", Fore.BLUE)
  jarvis.say("		Type 5 to check current giveaways from authors and publishers", Fore.BLUE)
  jarvis.say("		Type 6 to quit", Fore.BLUE)
  choice=jarvis.input("Your choice is: ", Fore.GREEN)
  
  if choice=='1':
    URL="https://www.goodreads.com/book/most_read"
    webbrowser.open(URL)
    return None
    
  elif choice=='2':
    URL="https://www.goodreads.com/search?q="
    title = jarvis.input("Tell me the title  or the ISBN of the book you are looking for:", Fore.GREEN)
    URL= GenerateURL(title, 'search', URL)
    webbrowser.open(URL)
    return None

  elif choice=='3':
    URL="https://www.goodreads.com/search?q="
    title = jarvis.input("Tell me the name of the author you are looking for:", Fore.GREEN)
    URL= GenerateURL(title, 'search title', URL)
    URL = URL + "&search%5Bsource%5D=goodreads&search_type=people&tab=people"
    webbrowser.open(URL)
    return None

  elif choice=='4':
    URL="https://www.goodreads.com/genres/"
    genre=jarvis.input("Tell me the name of the genre you would like to see:", Fore.GREEN)
    URL= GenerateURL(genre, 'suggestion', URL)
    webbrowser.open(URL)
    return None

  elif choice=='5':
    URL="https://www.goodreads.com/giveaway?sort=featured"
    webbrowser.open(URL)
    return None
  
  elif choice=='6':
    jarvis.say("Closed", Fore.RED)
    return None
  
  else:
    jarvis.say("Wrong Input", Fore.RED)
    return None


def GenerateURL(user_input, action, URL):
  #if action == 'suggestion' then the website link has '-' between words
  #but for search they use '+' token
  if action=='suggestion':
    token='-'
  else:
    token='+'
  words=user_input.split(' ')
  if len(words)<1:
    jarvis.say("Error. No input")
  elif len(words)==1:
    for word in words:
      URL= URL + word
  else:
    first=True
    for word in words:
      if first:
        URL= URL + word
        first = False
      else:
        URL= URL + token + word
  return URL
