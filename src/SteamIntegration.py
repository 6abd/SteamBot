import requests, pickle, os.path, re
from bs4 import BeautifulSoup


def checkDiscount(di):
    payload = {"appids": str(di)}
    r = requests.get("http://store.steampowered.com/api/appdetails/", params=payload)
    json = r.json()
    initial_price = json[str(di)]["data"]["price_overview"]["initial"]
    final_price = json[str(di)]["data"]["price_overview"]["final"]
    price_list = [initial_price, final_price]
    return price_list


def nameFinder(applistp, game_id):
    for i in range(0, len(applistp)):
        if game_id == applistp[i]["appid"]:
            return applistp[i]["name"]


def idFinder(applistp, user_input):
    ids = []
    names = []
    for i in range(0, len(applistp)):
        name = applistp[i]["name"]
        current_name = name.lower()
        user_input = re.sub(r'\W+', '', user_input)
        current_name = s = re.sub(r'\W+', '', current_name)
        if user_input.lower() in current_name:
            ids.append(applistp[i]["appid"])
            names.append(name)
    return ids, names


def wishlist(applistp, user_id, game_name, selname2, selid2):
    exact_name = nameFinder(applistp, selid2)

    if os.path.isfile("games.p"):
        big_dictionary = pickle.load(open("games.p", "rb"))
    else:
        big_dictionary = {}

    if not user_id in big_dictionary:
        big_dictionary[user_id] = [[], [], []]

    big_dictionary[user_id][0].append(selid2)
    big_dictionary[user_id][1].append(exact_name)
    big_dictionary[user_id][2].append(None)
    print(big_dictionary)
    pickle.dump(big_dictionary, open("games.p", "wb+"))
    return "Game successfully added"


def wishlistChecker():
    big_dictionary = pickle.load(open("games.p", "rb"))
    printed_discounts = []
    printed_prices = []
    if len(big_dictionary[0]) > 0:
        for i in range(0, len(big_dictionary[0])):
            if checkDiscount(big_dictionary[0][i])[0] > checkDiscount(big_dictionary[0][i])[1]:
                price_cut = checkDiscount(big_dictionary[0][i])[0] - checkDiscount(big_dictionary[0][i])[1]
                if big_dictionary[1][i] not in printed_discounts:
                    print(big_dictionary[1][i], "is", "$" + price_cut / 100, "USD off.")
                elif big_dictionary[1][i] in printed_discounts:
                    print("REMINDER:", big_dictionary[1][i], "is", "$" + price_cut / 100, "USD off.")
                printed_discounts.append(big_dictionary[1][i])


def applist():
    r2 = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
    json2 = r2.json()
    return json2["applist"]["apps"]


def printControls():
    print()


def gameSearch(selname, selid):
    dis = checkDiscount(selid)
    if dis[0] - dis[1] == 0:
        return "This game is not on sale. It costs ${}".format(dis[0] / 100)
    else:
        return "{} is {} USD off. The original price was: {} The final price is: {}".format(selname, ((dis[0] - dis[1]) / 100), (dis[0] / 100), (dis[1] / 100))



def appDesc(di):
    payload3 = {"appids": di}
    r3 = requests.get("https://store.steampowered.com/api/appdetails/", params=payload3)

    json3 = r3.json()
    desc = json3[str(di)]["data"]["short_description"]
    print(BeautifulSoup(desc).get_text("\n"))
    print(len(BeautifulSoup(desc).get_text("\n")))
    return BeautifulSoup(desc).get_text("\n")
