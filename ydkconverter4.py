import random
import json
from collections import Counter
from copy import deepcopy
from itertools import permutations
import requests
from pprint import pprint

card_data = requests.get(
    "https://db.ygoprodeck.com/api/v7/cardinfo.php").json()

mdtypes = [
    "Effect Monster",
    "Flip Effect Monster",
    "Flip Tuner Effect Monster",
    "Gemini Monster",
    "Normal Monster",
    "Normal Tuner Monster",
    "Pendulum Effect Monster",
    "Pendulum Flip Effect Monster",
    "Pendulum Normal Monster",
    "Pendulum Tuner Effect Monster",
    "Ritual Effect Monster",
    "Ritual Monster",
    "Spirit Monster",
    "Toon Monster",
    "Tuner Monster",
    "Union Effect Monster"]

edtypes = [
    "Fusion Monster",
    "Link Monster",
    "Pendulum Effect Fusion Monster",
    "Synchro Monster",
    "Synchro Pendulum Effect Monster",
    "Synchro Tuner Monster",
    "XYZ Monster",
    "XYZ Pendulum Effect Monster"]


def format_counter(deckcounter):
    out = ""
    for i in deckcounter:
        if deckcounter[i] == 1:
            out = out + f"\n{i}"
        else:
            out = out + f"\n{deckcounter[i]}x {i}"
    return out


def format_decklist(decklist):
    return format_counter(Counter(decklist))


def construct_deck(ydk_path):
    ydk_path = ydk_path if ydk_path[-4:] == ".ydk" else ydk_path + ".ydk"
    with open(ydk_path, "r") as deck_list:
        deck = deck_list.read().split("\n")
    # with open("cardinfo.json", "r") as card_data_json:
    #     card_data = json.loads(card_data_json.read())
    active_deck = []
    main_deck = []
    extra_deck = []
    side_deck = []
    for j in deck:
        if j == "#main":
            active_deck = main_deck
        elif j == "#extra":
            active_deck = extra_deck
        elif j == "!side":
            active_deck = side_deck
        elif j.isnumeric():
            for i in card_data["data"]:
                if i.get("id") == int(j):
                    active_deck.append(i["name"])
    return [main_deck, extra_deck, side_deck]


def to_ydk(cardlist, name):
    with open(name + ".ydk", "w") as file:
        card_data = requests.get(
            "https://db.ygoprodeck.com/api/v7/cardinfo.php").json()
        file.write("#created by ...\n")
        file.write("#main\n")
        for card in cardlist:
            for data in card_data["data"]:
                if data.get("name").lower() == card:
                    file.write(f"{('00000000'+str(data.get('id')))[-8:]}\n")
        file.write("#extra\n")
        file.write("!side")


def how_likely(condition, test_deck, sample_size):
    fulfilled = 0
    for i in range(sample_size):
        shuffled = deepcopy(test_deck)
        random.shuffle(shuffled)
        current_hand = []
        for j in range(5):
            current_hand.append(shuffled.pop())
        if condition(current_hand):
            fulfilled += 1
    return fulfilled / sample_size


def addtofirst(l, s):
    l[0] += s


def makebanlist():
    mdmon = []
    edmon = []
    spells = []
    traps = []
    fls = ' ' + input('forbidden: 0, limited: 1, semi: 2\n')
    ydk_path = input("What is your deck's name?\n")
    ydk_path = ydk_path if ydk_path[-4:] == ".ydk" else ydk_path + ".ydk"
    with open(ydk_path, "r") as deck_list:
        deck = list(set(deck_list.read().split("\n")))
    for card in deck:
        if card.isnumeric():
            for record in card_data["data"]:
                if record['id'] == int(card):
                    cardtype = record['type']
                    cardname = record['name']
                    if cardtype in mdtypes:
                        mdmon.append(card + fls + ' --' + cardname)
                    if cardtype in edtypes:
                        edmon.append(card + fls + ' --' + cardname)
                    if cardtype == 'Spell Card':
                        spells.append(card + fls + ' --' + cardname)
                    if cardtype in 'Trap Card':
                        traps.append(card + fls + ' --' + cardname)
    if mdmon:
        mdmon[0] += ' MAIN DECK MONSTERS START HERE'
    if edmon:
        edmon[0] += ' EXTRA DECK MONSTERS START HERE'
    if spells:
        spells[0] += ' SPELLS START HERE'
    if traps:
        traps[0] += ' TRAPS START HERE'
    with open('lflist.conf', 'w') as banlist:
        banlist.write(f"{chr(10).join(mdmon+edmon+spells+traps)}")


def searchcards():
    while True:
        cname = input('card name to search or type cock to quit\n').lower()
        if cname == 'cock':
            break
        for card in card_data["data"]:
            if card['name'].lower() == cname:
                pprint(card)
                break


if __name__ == '__main__':
    searchcards()
    deck = construct_deck(input("What is your deck's name?\n"))

    print(f"Main deck:\n{format_decklist(deck[0])}\n\n"
          f"Extra deck:\n{format_decklist(deck[1])}\n\n"
          f"Side deck:\n{format_decklist(deck[2])}")

    while input("Would you like to simulate an opening hand? Y/N(default)\n")[0].lower() == "y":
        shuffled_main = deepcopy(deck[0])
        random.shuffle(shuffled_main)
        for i in range(5):
            print(shuffled_main.pop())

    combolist = [["Rokket Tracer", "extender"], ["extender", "extender"]]
    categories = {
        "Rokket Tracer": "starter",
        "Quick Launch": "starterextender"
    }

    def iscombo(hand):
        # print(f"\nhand:\n{chr(10).join(hand)}")
        for a in combolist:
            for i in permutations(a):
                combo = deepcopy(list(i))
                # print(f"Checking for {combo}")
                combocards = []
                for j in hand:
                    # print(f"Checking if {j} is in combo")
                    if j in combo:
                        # print(f"{j} is in combo")
                        combo.remove(j)
                        combocards.append(j)
                    elif j in categories:
                        # print(f"{j} is a {categories[j]}")
                        for k in combo:
                            if k in categories[j]:
                                # print(f"{j} is in combo because it's a {k}")
                                combo.remove(k)
                                combocards.append(j)
                                break

                if len(combo) == 0:
                    # print(f"it's a combo!\n reason:\n{combocards} is {i}")
                    return True
            # print("not combo...")
        return False

    # print(how_likely(iscombo, deck[0], 1000))
