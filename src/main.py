import discord, SteamIntegration, pickle, os.path
from discord.ext import commands
from discord.utils import get
from discord.ext.tasks import loop

client = discord.Client()
steam = SteamIntegration
bot = commands.Bot(command_prefix='$')
channel = None


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@bot.command(name='search')
async def search(ctx):
    def check(m):
        return m.channel == ctx.message.channel and m.author == ctx.message.author

    await ctx.send("Enter a game: ")
    message = await ctx.bot.wait_for("message", timeout=60, check=check)
    game_name = message.content.lower()

    lis = steam.idFinder(steam.applist(), game_name)
    ids = lis[0]
    names = lis[1]

    nameprint = ""
    for i in range(0, len(names)):
        nameprint += str(i) + ".  " + names[i] + "\n"
    await ctx.send(nameprint + "\n" + "Select a game: ")
    num = await ctx.bot.wait_for("message", timeout=60, check=check)
    selname = names[int(num.content)]
    selid = ids[int(num.content)]
    await ctx.send(steam.gameSearch(selname, selid) + "\n\n" + "**Summary:**" + "\n\n" + steam.appDesc(selid))


@bot.command(name='wishlistadd')
async def add(ctx):
    def check2(m):
        return m.channel == ctx.message.channel and m.author == ctx.message.author

    await ctx.send("Enter a game: ")
    message = await ctx.bot.wait_for("message", timeout=60, check=check2)
    game_name2 = message.content.lower()

    lis2 = steam.idFinder(steam.applist(), game_name2)
    ids2 = lis2[0]
    names2 = lis2[1]

    nameprint2 = ""
    for i in range(0, len(names2)):
        nameprint2 += str(i) + ".  " + names2[i] + "\n"

    if len(nameprint2) > 1950:
        await ctx.send("Too many search results. Be more specific.")
        await add(ctx)
    elif len(nameprint2) == 0:
        await ctx.send("No results found. **Don't forget punctuation!**")
        await add(ctx)
    else:
        await ctx.send(nameprint2 + "\n" + "Select a game: ")
        num2 = await ctx.bot.wait_for("message", timeout=60, check=check2)
        selname2 = names2[int(num2.content)]
        selid2 = ids2[int(num2.content)]
        await ctx.send(steam.wishlist(steam.applist(), message.author.id, game_name2, selname2, selid2))


@bot.command(name='wishlistsub')
async def sub(ctx):
    def check3(m):
        return m.channel == ctx.message.channel and m.author == ctx.message.author

    await ctx.send("Enter any text for author verification: ")
    message = await ctx.bot.wait_for("message", timeout=60, check=check3)


    if os.path.isfile("games.p"):
        big_dictionary = pickle.load(open("games.p", "rb"))
        if len(big_dictionary[message.author.id][1]) == 0:
            await ctx.send("There are no games in your wishlist.")
            return
        else:
            user_id = ctx.message.author.id

            nameprint = ""
            for i in range(0, len(big_dictionary[user_id][1])):
                nameprint += str(i) + ". " + big_dictionary[user_id][1][i] + "\n\n"

            await ctx.send("Your wishlist: " + "\n\n" + nameprint + "\n")
            await ctx.send("Select a game: ")

        num3message = await ctx.bot.wait_for("message", timeout=60, check=check3)
        num3 = int(num3message.content)

        if num3 <= len(big_dictionary[user_id][0]) and num3 >= 0:

            big_dictionary[user_id][0].remove(big_dictionary[user_id][0][num3])
            big_dictionary[user_id][1].remove(big_dictionary[user_id][1][num3])
            del big_dictionary[user_id][2][num3]

            pickle.dump(big_dictionary, open("games.p", "wb"))
            await ctx.send("Game succesfully removed!")
        else:
            await ctx.send("Number must be visible in wishlist.")
    else:
        await ctx.send("Your wishlist is empty.")

@bot.command(name='wishlistview')
async def add(ctx):
    def check4(m):
        return m.channel == ctx.message.channel and m.author == ctx.message.author

    await ctx.send("Enter any text for author verification: ")
    message = await ctx.bot.wait_for("message", timeout=60, check=check4)

    big_dictionary = pickle.load(open("games.p", "rb"))
    if len(big_dictionary[message.author.id][1]) == 0:
        await ctx.send("There are no games in your wishlist.")
        return
    else:
        user_id = ctx.message.author.id

        nameprint = ""
        for i in range(0, len(big_dictionary[user_id][1])):
            nameprint += str(i) + ". " + big_dictionary[user_id][1][i] + "\n\n"

        await ctx.send("Your wishlist: " + "\n\n" + nameprint + "\n")



@loop(seconds=5)
async def wishlistChecker():
    big_dictionary = pickle.load(open("games.p", "rb"))
    if os.path.isfile("printed_discounts.p"):
        printed_discounts = pickle.load(open("printed_discounts.p", "rb"))
    else:
        printed_discounts = []

    # Loops through each user's ID list and checks for discounts

    for user in big_dictionary:
        if len(big_dictionary[user][0]) > 0:
            for i in range(0, len(big_dictionary[user][0])):
                game_prices = steam.checkDiscount(big_dictionary[user][0][i])
                check_name = big_dictionary[user][1][i]

                if game_prices[0] > game_prices[1]:
                    price_cut = game_prices[0] - game_prices[1]

                    if check_name not in printed_discounts:
                        big_dictionary[user][2][i] = game_prices[1]

                        await channel.send(
                            check_name + " is " + "$" + str(price_cut / 100) + " USD off. It costs $" + str(
                                game_prices[1] / 100) + " USD")
                        printed_discounts.append(check_name)

                    elif check_name in printed_discounts:
                        if game_prices[1] != big_dictionary[user][2][i]:
                            big_dictionary[user][2][i] = game_prices[1]
    pickle.dump(big_dictionary, open("games.p", "wb+"))
    pickle.dump(printed_discounts, open("printed_discounts.p", "wb+"))


@wishlistChecker.before_loop
async def before_wishlistChecker():
    global channel
    await bot.wait_until_ready()
    channel = bot.get_channel(885288821548269600)


wishlistChecker.start()
bot.run("API KEY HERE")
