import cloudscraper
import binpacking


# private info
accountName = "JustCallMeJick"
poesessid = ""

url = "https://www.pathofexile.com/character-window/get-stash-items"
league = "Affliction"
realm = "pc"
tabNamesToCheck = ["4", "2"]
tabIndices = []
gemQualityList = []

params = {
    'accountName': accountName,
    'league': league,
    'tabs': 1,
    'tabIndex': None,
    'public': None,
    'realm': realm
}
params = '&'.join([k if v is None else f"{k}={v}" for k, v in params.items()])
cookie = {
    'POESESSID': poesessid
}
scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance


def get_tab(index):
    return scraper.post(url, params=get_params(index), cookies=cookie).json()


def get_tabs():
    return scraper.post(url, params=params, cookies=cookie).json()


def is_gem(item):
    try:
        descText = item['descrText']
        return descText == "Place into an item socket of the right colour to gain this skill. Right click to remove from a socket." or descText == "This is a Support Gem. It does not grant a bonus to your character, but to skills in sockets connected to it. Place into an item socket connected to a socket containing the Skill Gem you wish to augment. Right click to remove from a socket."
    except:
        return False


def get_gem_quality(gem):
    for prop in gem["properties"]:
        if prop['name'] == "Quality":
            return int(prop['values'][0][0].replace("%", '').replace("+", ''))
    return 0


def get_params(index):
    paramsSingle = {
        'accountName': accountName,
        'league': league,
        'tabs': None,
        'tabIndex': index,
        'public': None,
        'realm': realm
    }
    return '&'.join([k if v is None else f"{k}={v}" for k, v in paramsSingle.items()])


class VendorSet:
    sum = 0
    qualities = []


try:
    allTabs = get_tabs()['tabs']
except:
    print("rate limited, try later")
    exit(-1)

for name in tabNamesToCheck:
    index = -1
    for tab in allTabs:
        if name == tab['n']:
            index = tab['i']
            break
    tabIndices.append(index)

tabsToCheck = []

for index in tabIndices:
    tabsToCheck.append(get_tab(index)['items'])

for tab in tabsToCheck:
    for item in tab:
        if is_gem(item):
            gemQualityList.append(get_gem_quality(item))


gemQualityList.sort(reverse=True)
bins = binpacking.to_constant_volume(gemQualityList, 40, upper_bound=40)

for bin in bins:
    if not sum(bin) == 40:
        bins.remove(bin)

uniqueList = []
for recipe in bins:
    if recipe not in uniqueList and sum(recipe) == 40:
        uniqueList.append(recipe)

for recipe in uniqueList:
    print("Qual: " + ', '.join(str(x) for x in recipe) + " x" + str(bins.count(recipe)))

print("===== list\n", gemQualityList, "\n", bins)