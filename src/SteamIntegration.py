import requests, pickle, os.path

def checkDiscount(di):
    payload = {"appids" : str(di)}
    r = requests.get("http://store.steampowered.com/api/appdetails/", params = payload)
    json = r.json()
    initial_price = json[str(di)]["data"]["price_overview"]["initial"]
    final_price = json[str(di)]["data"]["price_overview"]["final"]
    price_list = [initial_price, final_price]
    return price_list

def nameFinder(applist, game_id):
    for i in range(0, len(applist)):
        if game_id == applist[i]["appid"]:
            return applist[i]["name"]
        
def idFinder(applist, user_input):
    ids = []
    names = []
    for i in range(0, len(applist)):
        name = applist[i]["name"]
        current_name = name.lower()
        if user_input.lower() in current_name:
           ids.append(applist[i]["appid"])
           names.append(name)
    return ids, names

def idSelector(ids, names, user_selid):
    nameprint = ""
    for i in range(0, len(names)):
        nameprint += str(i) + ".  " + names[i] + "\n"
    num = int(input(nameprint + "\n" + "Select a game: "))
    selname = names[num]
    selid = ids[num]
    return selname, selid

def wishlist(applist):
    game_name = input("Enter game: ")
    ids2, names2= idFinder(applist, game_name)
    selname2, selid2 = idSelector(ids2, names2)
    exact_name = nameFinder(applist, selid2)
    if os.path.isfile("Pickle File"):
        big_list = pickle.load(open("Pickle File", "rb"))
    else:
        big_list = [[],[]]
    

    big_list[0].append(selid2)
    big_list[1].append(exact_name)
    print(big_list)
    pickle.dump(big_list, open("Pickle File", "wb+"))
        
def wishlistRemover():
    big_list = pickle.load(open("Pickle File", "rb"))
     
    
    game_name = input("Enter game: ")

    ids2 = []
    names2 = []
        
    for i in range(0, len(big_list[1])):
        name = big_list[1][i]
        current_name = name.lower()
        if game_name.lower() in current_name:
            ids2.append(big_list[0][i])
            names2.append(name)
               
    selname2, selid2 = idSelector(ids2, names2)
        
    for i in range(0, len(big_list[1])):
         if selid2 == big_list[0][i]:
            exact_name = big_list[1][i]
               

    big_list[0].remove(selid2)
    big_list[1].remove(exact_name)
    print(big_list)
    pickle.dump(big_list, open("Pickle File", "wb"))
                
def wishlistChecker():
    big_list = pickle.load(open("Pickle File", "rb"))
    printed_discounts = []
    printed_prices = []
    if len(big_list[0]) > 0:
        for i in range(0, len(big_list[0])):
            if checkDiscount(big_list[0][i])[0] > checkDiscount(big_list[0][i])[1]:
                price_cut = checkDiscount(big_list[0][i])[0] - checkDiscount(big_list[0][i])[1]
                if big_list[1][i] not in printed_discounts:
                    print(big_list[1][i], "is", price_cut / 100, "USD off.")
                elif big_list[1][i] in printed_discounts:
                    time.sleep(86400)
                    print("REMINDER:", big_list[1][i], "is", price_cut / 100, "USD off.")
                printed_discounts.append(big_list[1][i])
                
r2 = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
json2 = r2.json()
applist = json2["applist"]["apps"]
print("Press the 'CTRL' key to search for a game." + "\n" + "Press the 'Alt' key to add a game to your discount notification list." + "\n" + "Press the 'Shift' key to remove a game from your discount notification list." + "\n" + "Press the 'Q' key to quit the program")

def gameSearch(user_input, input_game):
    if user_input.lower() == "search":
        game_name = input_game
        lis = idFinder(applist, game_name)
        ids = lis[0]
        names = lis[1]
        selname, selid = idSelector(ids, names)
        if checkDiscount(selid)[0] - checkDiscount(selid)[1] == 0:
            return "This game is not on sale."
        else:
            return (selname, "is", (checkDiscount(selid)[0] - checkDiscount(selid)[1]) / 100, "USD, off," + "\n","The original price was:", checkDiscount(selid)[0] / 100, "The final price is:", checkDiscount(selid)[1] / 100)

def wishlistAdd(user_input2):
    if user_input2.lower() == "add":
            wishlist(applist)
        
def wishlistSub(user_input3):
    if user_input3.lower() == "remove":
            wishlistRemover()

    wishlistChecker()
