import random
from plugin import plugin
from colorama import Fore


def delay():  # method to pause after a series of actions have been completed.
    n = input("Press enter to continue")


def wiped_slate(player):  # resets all hands and bets
    player['hands'] = []
    player['suits'] = []
    player['bets'] = []
    return player


def pprinthand(hand, suit, type='visible'):  # returns hand as a string which may or may not be hidden.
    temphand = hand[:]
    for i in range(len(temphand)):
        if temphand[i] == 1 or temphand[i] == 11:
            temphand[i] = 'A'  # 1 or 11 is value of ace.
        temphand[i] = str(temphand[i]) + " of " + suit[i]
    if type == 'visible':
        return str(temphand)
    elif type == 'partially-visible':
        return '[' + str(temphand[0]) + ',hidden]'


def pprinthandlist(handlist, suitlist):  # returns handlist as a string
    newhandlist = []
    for i in range(len(handlist)):
        newhandlist.append(pprinthand(handlist[i], suitlist[i]))
    return str(newhandlist)


def blackjacksum(orig_hand):  # computes the sum by assuming appropriate value of Ace.
    hand = orig_hand[:]
    for i in range(len(hand)):
        if str(hand[i]) in 'JQK':  # converts face card to their value,that is,10.
            hand[i] = 10
    if sum(hand) <= 11:  # of Ace card(either 1 or 11) acc. to the sum.
        for i in range(len(hand)):
            if hand[i] == 1:
                hand[i] = 11
                orig_hand[i] = 11
                break
    elif sum(hand) > 21:
        for i in range(len(hand)):
            if hand[i] == 11:
                hand[i] = 1
                orig_hand[i] = 1
                break
    return sum(hand), orig_hand


def move(hand, suit, cards, suits,
         bet):  # Here, hand is a nested list inside a list. It is a list of all hands of a player.
    # Player can have multiple hands if he/she chooses to split.
    sum_, hand[0] = blackjacksum(hand[0])
    print("Your hand is", pprinthand(hand[0], suit[0]))
    print("Your sum is", sum_)
    print('---------------------------')
    # checks for bust or blackjack.
    if sum_ > 21:
        print("You got busted!")
        return hand, suit, bet
    elif sum_ == 21 and len(hand) == 2:
        print("Blackjack!")
        return hand, suit, bet

    while True:
        choice = input("Press H to Hit, S to Stand, D to Double-Down, P to sPlit\n")
        if choice in ['H', 'h']:
            newcard = random.choice(cards)
            newsuit = random.choice(suits)
            print("Newcard is", str(newcard) + " of " + newsuit)
            hand[0].append(newcard)
            suit[0].append(newsuit)
            print("Updated hand is", pprinthand(hand[0], suit[0]))
            sum_, hand[0] = blackjacksum(hand[0])
            hand, suit, bet = move(hand, suit, cards, suits, bet)
            return hand, suit, bet

        elif choice in ['S', 's']:
            return hand, suit, bet

        elif choice in ['D', 'd']:
            newcard = random.choice(cards)
            print("Newcard is", newcard)
            newsuit = random.choice(suits)
            hand[0].append(newcard)
            suit[0].append(newsuit)
            print("Updated hand is", pprinthand(hand[0], suit[0]))
            sum_, hand[0] = blackjacksum(hand[0])
            print("Your sum is", sum_)
            if sum_ > 21:
                print("You got busted!")
            bet[0] = bet[0] * 2
            print("Your new bet is", bet[0])
            return hand, suit, bet

        elif choice in ['P', 'p']:
            if hand[0][0] == hand[0][1]:
                if not hand[0][0] == 1:
                    splitHand1 = [[0, 0]]
                    splitHand2 = [[0, 0]]
                    splitSuit1 = [[0, 0]]
                    splitSuit2 = [[0, 0]]
                    newcard1 = random.choice(cards)
                    newsuit1 = random.choice(suits)
                    print("Newcard for first split is", str(newcard1) + " of " + newsuit1)
                    newcard2 = random.choice(cards)
                    newsuit2 = random.choice(suits)
                    print("Newcard for second split is", str(newcard2) + " of " + newsuit2)
                    splitHand1[0][0] = hand[0][0]
                    splitHand2[0][0] = hand[0][1]
                    splitHand1[0][1] = newcard1
                    splitHand2[0][1] = newcard2
                    splitSuit1[0][0] = suit[0][0]
                    splitSuit2[0][0] = suit[0][1]
                    splitSuit1[0][1] = newsuit1
                    splitSuit2[0][1] = newsuit2
                    print("Split hands are", pprinthand(splitHand1[0], splitSuit1[0]), ", ",
                          pprinthand(splitHand2[0], splitSuit2[0]))
                    sum1, splitHand1[0] = blackjacksum(splitHand1[0])
                    sum2, splitHand2[0] = blackjacksum(splitHand2[0])
                    print("Your sum for split 1 is", sum1)
                    print("Your sum for split 2 is", sum2)
                    bet1 = bet[:]
                    bet2 = bet[:]
                    splitHand1, splitSuit1, bet1 = move(splitHand1, splitSuit1, cards, suits, bet1)
                    splitHand2, splitSuit2, bet2 = move(splitHand2, splitSuit2, cards, suits, bet2)
                    splitHand1.extend(splitHand2)  # converting both hands to a single list
                    splitSuit1.extend(splitSuit2)
                    bet1.extend(bet2)  # converting both bets to a single list
                    return splitHand1, splitSuit1, bet1
                else:
                    print("Sorry,you can't split aces")
                    hand, suit, bet = move(hand, suit, cards, suits, bet)
                    return hand, suit, bet
            else:
                print("Sorry, you can only split hands with identical cards")
                hand, suit, bet = move(hand, suit, cards, suits, bet)
                return hand, suit, bet
        else:
            print("Please try again with a valid choice.")


@plugin('blackjack')
def blackjack(jarvis, s):
    jarvis.say("Welcome to the casino! Let's play blackjack!", Fore.GREEN)
    player = {"hands": [], "suits": [], "bets": [], 'profit': []}
    cards = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
    suits = ['spades', 'hearts', 'diamonds', 'clubs']
    choice = 'y'
    delay()

    # Instructions
    jarvis.say('How to play:', Fore.GREEN)
    jarvis.say('-->The goal of blackjack is to beat the dealer\'s hand without going over 21.', Fore.CYAN)
    jarvis.say('-->Face cards are worth 10. Aces are worth 1 or 11, whichever makes a better hand.', Fore.CYAN)
    jarvis.say('-->Each player starts with two cards, one of the dealer\'s cards is hidden until the end.', Fore.CYAN)
    jarvis.say('-->To \'Hit\' is to ask for another card. To \'Stand\' is to hold your total and end your turn.',
               Fore.CYAN)
    jarvis.say('-->If you go over 21 you bust, and the dealer wins regardless of the dealer\'s hand.', Fore.CYAN)
    jarvis.say('-->If you are dealt 21 from the start (Ace & 10), you got a blackjack.', Fore.CYAN)
    jarvis.say('-->Blackjack means you win 1.5 the amount of your bet.', Fore.CYAN)
    jarvis.say('-->Dealer will hit until his/her cards total 17 or higher.', Fore.CYAN)
    jarvis.say('-->Doubling is like a hit, only the bet is doubled and you only get one more card.', Fore.CYAN)
    jarvis.say('-->Split can be done when you have two of the same card - the pair is split into two hands.', Fore.CYAN)
    jarvis.say('-->Splitting also doubles the bet, because each new hand is worth the original bet.', Fore.CYAN)
    jarvis.say('-->You cannot split two aces.', Fore.CYAN)
    jarvis.say('-->You can double on a hand resulting from a split, tripling or quadrupling you bet.', Fore.CYAN)

    while choice in "Yy":
        jarvis.say('Shuffling the cards....', Fore.BLUE)
        jarvis.say("Let's start the game!", Fore.BLUE)
        # Bets
        jarvis.say("How much are you betting?", Fore.BLUE)
        bet = jarvis.input_number()
        player['bets'].append(bet)
        delay()
        jarvis.say('---------------------------')

        # Cards
        jarvis.say("Dealing the cards............", Fore.BLUE)
        jarvis.say("Your cards....", Fore.BLUE)
        hand = [random.choice(cards), random.choice(cards)]
        suit = [random.choice(suits), random.choice(suits)]
        player["hands"].append(hand)
        player["suits"].append(suit)
        jarvis.say(pprinthand(hand, suit))
        delay()
        jarvis.say('---------------------------')

        # Dealer's cards
        dealerhand = [random.choice(cards), random.choice(cards)]
        dealersuit = [random.choice(suits), random.choice(suits)]
        jarvis.say("Dealer hand: " + pprinthand(dealerhand, dealersuit, type='partially-visible'), Fore.MAGENTA)
        delay()
        jarvis.say('---------------------------')

        # Players' moves
        jarvis.say("It's your turn, make your choice!", Fore.BLUE)
        player['hands'], player['suits'], player['bets'] = move(player['hands'], player['suits'], cards, suits,
                                                                player['bets'])
        jarvis.say("Your hands and respective bets for this round are:", Fore.BLUE)
        jarvis.say(pprinthandlist(player['hands'], player['suits']) + "      " + str(player['bets']), Fore.BLUE)
        delay()
        jarvis.say('---------------------------')

        # Dealer's moves
        jarvis.say("Dealer hand: " + pprinthand(dealerhand, dealersuit), Fore.MAGENTA)
        dealersum, dealerhand = blackjacksum(dealerhand)
        jarvis.say("Dealer's sum is " + str(dealersum), Fore.MAGENTA)
        while dealersum < 17 or (
                dealersum == 17 and 11 in dealerhand):  # condition which determines if dealer hits or not.
            jarvis.say("Dealer draws another card", Fore.MAGENTA)
            dealerhand.append(random.choice(cards))
            dealersuit.append(random.choice(suits))
            jarvis.say("Newcard is " + str(dealerhand[-1]) + " of " + str(dealersuit[-1]), Fore.MAGENTA)
            dealersum, dealerhand = blackjacksum(dealerhand)
            jarvis.say("Dealer's sum is " + str(dealersum), Fore.MAGENTA)
            jarvis.say("Dealer's hand is " + pprinthand(dealerhand, dealersuit), Fore.MAGENTA)
        delay()
        jarvis.say('---------------------------')

        # Profit Calculation
        jarvis.say("Let's see your results ", Fore.BLUE)
        for j in range(len(player['hands'])):
            hand = player['hands'][j]
            suit = player['suits'][j]
            bet = player['bets'][j]
            sum_, hand = blackjacksum(hand)
            dealersum, dealerhand = blackjacksum(dealerhand)
            jarvis.say("For the hand- " + pprinthand(hand, suit) + '  sum is-' + str(sum_), Fore.BLUE)
            if len(hand) == 2 and sum_ == 21:
                jarvis.say("Blackjack!", Fore.BLUE)
                profit = bet * 1.5
                player['profit'].append(bet * 1.5)
            elif sum_ > 21:
                jarvis.say("Busted", Fore.BLUE)
                profit = bet * -1
                player['profit'].append(bet * -1)
            elif dealersum > 21:
                jarvis.say("Dealer Busted", Fore.BLUE)
                profit = bet * 1
                player['profit'].append(bet * 1)
            elif dealersum > sum_:
                jarvis.say("You lost", Fore.BLUE)
                profit = bet * -1
                player['profit'].append(bet * -1)
            elif sum_ > dealersum:
                jarvis.say("You win", Fore.BLUE)
                profit = bet * 1
                player['profit'].append(bet * 1)
            elif sum_ == 21 and dealersum == 21 and len(dealerhand) == 2 and len(hand) > 2:
                jarvis.say("You lost", Fore.BLUE)
                profit = bet * -1
                player['profit'].append(bet * -1)
            elif sum_ == dealersum:
                jarvis.say("Push", Fore.BLUE)
                profit = bet * 0
                player['profit'].append(bet * 0)
            jarvis.say("Profit is- " + str(profit), Fore.BLUE)
        players = wiped_slate(player)
        choice = jarvis.input("Do you wish to play another round?Y/n \n", Fore.GREEN)

    jarvis.say("OK then, Let's see the results", Fore.GREEN)
    jarvis.say('---------------------------')
    # total profit calculation
    profit = sum(player['profit'])
    if profit >= 0:
        jarvis.say("Your total profit is " + str(profit), Fore.GREEN)
    else:
        jarvis.say("Your total loss is " + str(profit * -1), Fore.GREEN)
    jarvis.say("Goodbye, Let's play again sometime!", Fore.GREEN)
