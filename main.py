import random
ranks = ["2","3","4","5","6","7","8","9","10","Jack","Queen","King","Ace"]
suits = ["Diamonds","Spades","Hearts","Clubs"]

class HandData:
    def __init__(self,cards: list,hand):
        self.hand = hand
        self.cards = cards
        self.score = 0
    def calcScore(self):
        if self.hand != None:
            for i in self.cards:
                self.score += i.value
    def __str__(self):
        return f"{utils.cardObjectsToStrings(self.cards)} {self.hand}"
class Card:
    def __init__(self,rank,suit):
        global ranks
        self.rank = rank
        self.suit = suit
        self.value = ranks.index(rank) + 2
        self.string = f"{self.rank} of {self.suit}"

    def __str__(self):
        return self.string
    
class DeckClass:
    def __init__(self,ranks,suits):
        self.ranks = ranks
        self.suits = suits
        self.restoreDeck()
        self.shuffle()

    def restoreDeck(self):
        self.deck = []
        for suit in self.suits:
            for rank in self.ranks:
                self.deck.append(Card(rank,suit))

    def shuffle(self):
        random.shuffle(self.deck)

    def drawCards(self,amount):
        cardsDrawn = []
        for _ in range(amount):
            cardsDrawn.append(self.deck[0])
            self.deck.pop(0)
        return cardsDrawn
    
    def __str__(self):
        return str(utils.cardObjectsToStrings(self.deck))

class GlobalPlayerData: #yes, I do understand that this can be replaced with a dictionary, I just don't care
    def __init__(self,chips,bot,blind):
        self.chips = chips
        self.bot = bot
        self.blind = blind

class LocalPlayerData:
    def __init__(self,player):
        self.player = player
        self.folded = False
        self.__cards = []
        self.bet = 0
        self.hand = None

    def accessCards(self,change = None):
        if change != None:
            self.__cards = change
        return self.__cards
    
class Utilities:
    def cardValueSort(self,cards):
        #Bubble Sort (ascending)
        end = False
        sortedList = cards.copy()
        while not end:
            end = True
            for i in range(len(sortedList)):
                if i + 1 != len(sortedList):
                    if sortedList[i].value > sortedList[i+1].value:
                        end = False
                        swapNum = sortedList[i]
                        sortedList[i] = sortedList[i+1]
                        sortedList[i+1] = swapNum
        return sortedList
    
    def cardObjectsToStrings(self,cards): 
        returnValue = []
        for i in cards:
            returnValue.append(i.string)
        return returnValue 
    
    def sortPlayersInOrder(self,players: list) -> list:
        playerOrder = players.copy()
        for _ in range(len(playerOrder)):
            if players[playerOrder[0]].blind == "small":
                break
            playerOrder.append(playerOrder[0])
            playerOrder.remove(playerOrder[0]) # remove() removes the first occurence so we just placing the first index to the end
        return playerOrder
    
    def getBlinds(self,players:list,local:bool = False) -> tuple:
        smallBlind = "" 
        bigBlind = ""
        for i in players:
            if local:
                if i.player.blind == "small":
                    smallBlind = i
                elif i.player.blind == "big":
                    bigBlind = i
            else:
                if i.blind == "small":
                    smallBlind = i
                elif i.blind == "big":
                    bigBlind = i
        return (smallBlind,bigBlind)

utils = Utilities()   

def testbot(me,otherPlayers,pot,communityCards): #debug
    pass

players = [GlobalPlayerData(500,testbot,"small"),GlobalPlayerData(500,testbot,"big"),GlobalPlayerData(500,testbot,None)]

def restart():
    global ranks
    global suits
    global players #assigning blinds. really crappy code but i don't care
    if len(players) > 2:
        order = utils.sortPlayersInOrder(players)
        order[0].blind = None
        order[1].blind = "small"
        order[2].blind = "big"
    Game(players,DeckClass(ranks,suits))

class Game:
    def __init__(self,players,deck):
        self.update("pre-flop")

    def update(self,stage):
        match stage:
            case "pre-flop":
                self.update("flop")

            case "flop":
                self.update("turn")

            case "turn":
                self.update("river")

            case "river":
                self.update("showdown")

            case "showdown":
                pass

            case _:
                raise Exception(f"Invalid update stage value, {stage}, at {self}")
            
    def checkHand(self,cards):
        
        global ranks
        global suits
        hands = []
        handNames= ["Pair","Two Pair","Three of a Kind","Straight","Flush","Full House","Four of a Kind","Straight Flush"]

        #pairs and three/four of a kinds
        kindHands = []
        kindsNames = [None,"Pair","Three of a Kind","Four of a Kind"]

        for i in cards:
            cardsNoI = cards.copy()
            cardsNoI.remove(i)
            handKinds = HandData([],None)
            for ii in cardsNoI:
                if ii.rank == i.rank:
                    handKinds.hand = kindsNames[kindsNames.index(handKinds.hand) + 1]
                    handKinds.cards.append(ii)
            kindHands.append(handKinds)
        hands += kindHands


        # straights
        def straightCheck(handCards):
            bestHandFound = HandData([],"Straight")
            cardList = utils.cardValueSort(handCards.copy()) 
            cardList.reverse()
            #creates a list of tuples consisting of card objects and value (for straights to be 1 and 14)
            for index in range(len(cardList)):
                object = cardList[index]
                cardList[index] = (object,object.value)
                if object.rank == "Ace":
                    cardList.append((object,1))
            for index in range(len(cardList) - 1):

                difference = cardList[index][1] - cardList[index + 1][1]
                if difference == 1:
                    bestHandFound.hand.append(cardList[index][0])
                if difference < 0:
                    raise Exception(f'Invalid straight difference, "{difference}", at {self}, with the cards being {handCards}')
                if difference == 0:
                    pass
                else:
                    bestHandFound.hand = []
            if len(bestHandFound.hand) == 5:
                return bestHandFound
            return None
    
        bestHandStraights = straightCheck(cards)

        #flushes and sFlushes TODO


        bestHandFlushes = HandData([],None)
        flushSuits = {}
        sFlushSuits = {}
        flushSpecial = utils.cardValueSort(cards.copy())
        flushSpecial.reverse()

        for suit in suits:
            flushSuits[suit] = []
            sFlushSuits[suit] = []

        for suit in flushSuits:
            for card in flushSpecial:
                if card.suit == suit:
                    sFlushSuits[suit].append(card)
                    if len(flushSuits[suit]) < 5:
                        flushSuits[suit].append(card)


        
