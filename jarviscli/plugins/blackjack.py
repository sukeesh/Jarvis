import random
from plugin import plugin
import sys
def clear_lines(number=1):
    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'
    for i in range(number):
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)
def delay():
    n=input("Press enter to continue")
def wiped_slate(players):
    for player in players:
        player['hands']=[]
        player['suits']=[]
        player['bets']=[]
    return players
def pprinthand(hand,suit,type='visible'):
    temphand=hand[:]
    for i in range(len(temphand)):
        if temphand[i]==1 or temphand[i]==11:
            temphand[i]='A'           # 1 or 11 is value of ace.
        elif temphand[i]==10:
            temphand[i]='F'           # 10 is value of all face cards.
        temphand[i]=str(temphand[i])+" of "+suit[i]
    if type=='visible':
        return str(temphand)
    else:
        return '['+str(temphand[0])+',hidden]'
def pprinthandlist(handlist,suitlist):
    newhandlist=[]
    for i in range(len(handlist)):
        newhandlist.append(pprinthand(handlist[i],suitlist[i]))
    return str(newhandlist)
##################################
def blackjacksum(hand):# computes the sum by assuming appropriate value
    if sum(hand)<=11:  # of Ace card(either 1 or 11) acc. to the sum.
        for i in range(len(hand)):
            if hand[i]==1:
                hand[i]=11
                break
    elif sum(hand)>21:
        for i in range(len(hand)):
            if hand[i] == 11:
                hand[i] = 1
                break
    return sum(hand),hand
###################################
def move(hand,suit,cards,suits,bet):# Here, hand is a nested list inside a list. It is a list of all hands of a player.
    sum_,hand[0]=blackjacksum(hand[0])
    print("Your hand is", pprinthand(hand[0],suit[0]))
    print("Your sum is", sum_)
    if sum_>21:
        print("You got busted!")
        return hand,suit, bet
    elif sum_==21 and len(hand)==2:
        print("Blackjack!")
        return hand,suit, bet
    choice=input("Press H to Hit, S to Stand, D to Double-Down, P to sPlit")

    if choice in['H','h']:
        newcard=random.choice(cards)
        newsuit = random.choice(suits)
        print("Newcard is",str(newcard)+" of "+newsuit)
        hand[0].append(newcard)
        suit[0].append(newsuit)
        print("Updated hand is",pprinthand(hand[0],suit[0]))
        sum_, hand[0] = blackjacksum(hand[0])
        hand,suit,bet=move(hand,suit,cards,suits,bet)
        return hand,suit,bet

    if choice in['S','s']:
        return hand,suit,bet

    if choice in['D','d']:
        newcard = random.choice(cards)
        print("Newcard is", newcard)
        newsuit = random.choice(suits)
        hand[0].append(newcard)
        suit[0].append(newsuit)
        print("Updated hand is", pprinthand(hand[0],suit[0]))
        sum_, hand[0] = blackjacksum(hand[0])
        print("Your sum is", sum_)
        if sum_ > 21:
            print("You got busted!")
        bet[0]=bet[0]*2
        print("Your new bet is", bet[0])
        return hand,suit,bet

    if choice in['P','p']:
        if hand[0][0]==hand[0][1]:
            if not hand[0][0]==1:
                splitHand1=[[0,0]]
                splitHand2=[[0,0]]
                splitSuit1 = [[0, 0]]
                splitSuit2 = [[0, 0]]
                newcard1=random.choice(cards)
                newsuit1 = random.choice(suits)
                print("Newcard for first split is",str(newcard1)+" of "+newsuit1)
                newcard2 = random.choice(cards)
                newsuit2 = random.choice(suits)
                print("Newcard for second split is", str(newcard2)+" of "+newsuit2)
                splitHand1[0][0] = hand[0][0]
                splitHand2[0][0] = hand[0][1]
                splitHand1[0][1] = newcard1
                splitHand2[0][1] = newcard2
                splitSuit1[0][0] = suit[0][0]
                splitSuit2[0][0] = suit[0][1]
                splitSuit1[0][1] = newsuit1
                splitSuit2[0][1] = newsuit2
                print("Split hands are",pprinthand(splitHand1[0],splitSuit1[0]),", ",pprinthand(splitHand2[0],splitSuit2[0]))
                sum1,splitHand1[0] = blackjacksum(splitHand1[0])
                sum2, splitHand2[0] = blackjacksum(splitHand2[0])
                print("Your sum for split 1 is", sum1)
                print("Your sum for split 2 is", sum2)
                bet1=bet[:]
                bet2 = bet[:]
                splitHand1,splitSuit1,bet1=move(splitHand1,splitSuit1,cards,suits,bet1)
                splitHand2,splitSuit2,bet2=move(splitHand2,splitSuit2,cards,suits,bet2)
                splitHand1.extend(splitHand2)#converting both hands to a single list
                splitSuit1.extend(splitSuit2)
                bet1.extend(bet2)#converting both bets to a single list
                return splitHand1,splitSuit1,bet1
            else:
                print("Sorry,you can't split aces")
                hand,suit,bet=move(hand,suit,cards,suits,bet)
                return hand,suit,bet
        else:
            print("Sorry, you can only split hands with identical cards")
            hand,suit, bet = move(hand,suit, cards,suits, bet)
            return hand,suit, bet
############################################################################
# # Main driver code
@plugin('blackjack')
def blackjack(jarvis,s):
    jarvis.say("Welcome to the casino! Let's play blackjack!")
    n=jarvis.input_number("How many players are playing?",rtype=int)
    players=[]
    dealerhand=[]
    for i in range(n):
        name=jarvis.input("Enter name, Player{}".format(i+1))
        players.append({"name":name,"hands":[],"suits":[],"bets":[],'profit':[]})
    cards=[1,2,3,4,5,6,7,8,9,10,10,10,10]
    suits=['spades','hearts','diamonds','clubs']
    choice='y'
    delay()
    while choice in "Yy":
        jarvis.say("Let's start the game!")
        ########### Bets
        for i in range(n):
            jarvis.say(players[i]["name"],",How much are you betting?")
            bet=jarvis.input()
            players[i]["bets"].append(bet)
        ########### Cards
        jarvis.say("Dealing the cards............")
        for i in range(n):
            jarvis.say(players[i]["name"],"Your cards....")
            hand=[random.choice(cards),random.choice(cards)]
            suit=[random.choice(suits),random.choice(suits)]
            players[i]["hands"].append(hand)
            players[i]["suits"].append(suit)
            jarvis.say(pprinthand(hand,suit))
        delay()
        ########### Dealer's cards
        dealerhand=[random.choice(cards),random.choice(cards)]
        dealersuit=[random.choice(suits),random.choice(suits)]
        jarvis.say("Dealer hand: "+pprinthand(dealerhand,dealersuit,type='partially-visible'))
        delay()
        ########### Players' moves
        for i in range(n):
            jarvis.say("It's your turn, "+ players[i]['name'])
            players[i]['hands'],players[i]['suits'],players[i]['bets']=move(players[i]['hands'],players[i]['suits'],cards,suits,players[i]['bets'])
            jarvis.say("Your hands and respective bets for this round are:")
            jarvis.say(pprinthandlist(players[i]['hands'],players[i]['suits'])+"      "+str(players[i]['bets']))
            delay()
        ########### Dealer's moves
        jarvis.say("Dealer hand: "+pprinthand(dealerhand,dealersuit))
        dealersum,dealerhand=blackjacksum(dealerhand)
        jarvis.say("Dealer's sum is "+str(dealersum))
        while dealersum<17 or (dealersum==17 and 11 in dealerhand) :
            jarvis.say("Dealer draws another card")
            dealerhand.append(random.choice(cards))
            dealersuit.append(random.choice(suits))
            jarvis.say("Newcard is"+ str(dealerhand[-1])+" of "+str(dealersuit[-1]))
            dealersum,dealerhand=blackjacksum(dealerhand)
            jarvis.say("Dealer's sum is "+ str(dealersum))
            jarvis.say("Dealer's hand is "+ pprinthand(dealerhand,dealersuit))
        delay()
        ########### Profit Calculation
        for i in range(n):
            jarvis.say('---------------------------')
            jarvis.say("Let's see your results "+players[i]['name'])
            for j in range(len(players[i]['hands'])):
                hand=players[i]['hands'][j]
                suit=players[i]['suits'][j]
                bet=players[i]['bets'][j]
                sum_,hand=blackjacksum(hand)
                dealersum,dealerhand=blackjacksum(dealerhand)
                jarvis.say("For the hand- "+pprinthand(hand,suit)+'  sum is-'+str(sum_))
                if len(hand)==2 and sum_==21:
                    jarvis.say("Blackjack!")
                    profit=bet*1.5
                    players[i]['profit'].append(bet*1.5)
                elif sum_>21:
                    jarvis.say("Busted")
                    profit = bet * -1
                    players[i]['profit'].append(bet * -1)
                elif dealersum>21:
                    jarvis.say("Dealer Busted")
                    profit = bet * 1
                    players[i]['profit'].append(bet*1)
                elif dealersum>sum_:
                    jarvis.say("You lost")
                    profit = bet * -1
                    players[i]['profit'].append(bet * -1)
                elif sum_>dealersum:
                    jarvis.say("You win")
                    profit = bet * 1
                    players[i]['profit'].append(bet * 1)
                elif sum_==21 and dealersum==21 and len(dealerhand)==2 and len(hand)>2:
                    jarvis.say("You lost")
                    profit = bet * -1
                    players[i]['profit'].append(bet * -1)
                elif sum_==dealersum:
                    jarvis.say("Push")
                    profit = bet * 0
                    players[i]['profit'].append(bet * 0)
                jarvis.say("Profit is- "+str(profit))
        players=wiped_slate(players)
        choice=jarvis.input("Do you wish to play another round?Y/n")
    jarvis.say("OK then, Let's see the results")
    for i in range(n):                     # total profit calculation
        name=players[i]['name']
        profit=sum(players[i]['profit'])
        if profit>=0:
            jarvis.say(name+" , your total profit is "+str(profit))
        else:
            jarvis.say(name+  " , your total loss is "+ str(profit * -1))



