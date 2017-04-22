## mine information from web pages ##

# import

from pyquery import PyQuery as pq
from lxml import html
from lxml import etree
import re

# constants

wiki_base = "http://en.wikipedia.org"
wiki = wiki_base + "/wiki/Category:Video_game_lists_by_platform"
wiki2 = wiki_base + "/w/index.php?title=Category:Video_game_lists_by_platform&pagefrom=Windows%0AIndex+of+Windows+games+%28P%29#mw-pages"

synonyms = { "3DO Interactive Multiplayer" : "3DO",  "Enix home computer" : "Enix",
             "Nintendo Entertainment System" : "NES", "Super Nintendo Entertainment System" : "SNES",
             "Nintendo GameCube" : "GameCube", 
             "PC Engine CD" : "TurboGrafx-16", "PC Engine" : "TurboGrafx-16", "Windows" : "PC",
             "Windows Mobile Professional" : "Pocket PC", "PlayStation Portable" : "PSP",
             "PlayStation 2" : "PS2", "PlayStation 3" : "PS3", "PlayStation 4" : "PS4",
             "Macintosh" : "Mac", "PlayStation Vita" : "Vita" }

genres = ["educational", "adventure", "golf", "shogi", "role-playing", "open-world", "shooter",
          "visual novel", "puzzle", "shoot 'em up", "racing", "maze", "card", "tennis", "strategy"]

# functions

def text(e, no_sup = False):
    """convert html element to text, recursively"""
    if (type(e) == etree._ElementUnicodeResult):
        return e
    if (type(e) == pq):
        return "".join([text(c, no_sup) for c in e.contents()])
    else:   # (type(e) == html.HtmlElement)
        try:
            if (e is None):
                return ""
            if ("style" in e.keys() and "display:none" in e.attrib["style"]):
                return ""
            if (e.tag == "br"):
                return "\n"
            elif (e.tag == "span" and e.attrib.get("class") == "flagicon"):
                abbrev = { "United States" : "US", "Japan" : "JP", "South Korea" : "SK",
                           "European Union" : "EU", "Australia" : "AU", "Brazil" : "BR",
                           "Europe" : "EU", "Mexico" : "MX", "Taiwan" : "TW" }
                region = e.find("a").attrib.get("title")
                if (region in abbrev):
                    region = abbrev[region]
                return " " + region + "\n"
            elif (e.tag == "sup" and no_sup):
                return ""
            elif (e.text_content() and (e.tag == "i" or e.tag == "a" or
                        (e.tag == "td" or e.tag == "th") or
                        (e.tag == "li" or e.tag == "dt"))):
                return e.text_content()
            elif (e.text_content() and (e.tag == "sup")):
                return " " + e.text_content()
            else:
                return "".join([text(c, no_sup) for c in e.getchildren()])
        except AttributeError:
            print("attr")
            return e.text or "".join([text(c, no_sup) for c in e.getchildren()])
        except BaseException:
            print("bas")
            return ""

def first(text):
    """if text is composed of multiple lines, only take first"""
    return text.splitlines()[0] if text != "" else ""
    
def clean(text):
    """cleans text string by removing (date), - company"""
    # re.sub(r'\s*\(\d{4}\)\s*', '', "text")
    return text

def reorder(text):
    """reorder strings that are in format [title, The] to [The title]"""
    m = re.match("([\w ]+), The$", text)
    return "The " + m.group(1) if m else text

def year(text, verbose = True):
    """interpret date data, convert to mm/dd/yyyy format"""
    conv = { "January" : 1, "February" : 2, "March" : 3, "April" : 4, "May" : 5, "June" : 6,
             "July" : 7, "August" : 8, "September" : 9, "October" : 10, "November" : 11, "December" : 12 }
    if (len(text.splitlines()) > 1):
        return " | ".join([year(t) for t in text.splitlines() if t != ""])
    regions = re.search(r"(([A-Z]{2}(, )?)+)", text)
    reg_str = " " + regions.group(1) if regions else ""
    date0 = re.search(r"(\d+)/(\d+)/(\d+)", text)
    if (date0):
        return date0.group(3) + reg_str
    date1 = re.search(r"(\w+) (\d+), (\d+)", text)
    if (date1):
        return date1.group(3) + reg_str
    date2 = re.search(r"(\w+)-(\w+)-(\w+)", text)
    if (date2):
        return date2.group(1) + reg_str
    date3 = re.search(r"(\d{4})", text)
    if (date3):
        return date3.group(1) + reg_str
    #if (text != "" and verbose):
    #    print("can't convert date: " + text)
    return "" #+ reg_str

def update_games(games, name, td, col):
    """update games info with new data, return games and name"""
    low = col.lower()
    if (name == ""):
        if ((low.find("title") != -1 or low.find("name") != -1 or
             low.find("game") != -1) and text(td) != "—"):
            name = reorder(first(text(td, no_sup = True)))
            (games, name) = parse_name(games, name) #games[name] = ["",] * 7
    else:
        t = text(td)
        yr = year(t, verbose = False)
        if (low.find("year") != -1 or low.find("date") != -1 or
            col == "Release" or col == "Released" or col == "First released"):
            games[name][0] = yr
        if (low.find("genre") != -1):
            games[name][1] = t
        if (low.find("develop") != -1 or low.find("program") != -1):
            games[name][2] = t
        if (low.find("publish") != -1):
            games[name][3] = " | ".join( \
                [t.strip() for t in text(td).split("\n") if t != ""])
        if (low.find("region") != -1):
            games[name][5] = t
        if (low.find("esrb") != -1):
            games[name][6] = t
        if (low.find("details") != -1):
            g = [genre for genre in genres if genre in t.lower()]
            if (not(len(g) < 1)):
                games[name][1] += g[0]
            m = re.search(r'[Bb]y ([\w\s]+)[\.,\(\)]', t)
            if (m):
                games[name][2] = m.group(1).strip()
        # check if 'yes' or checked or release date given
        if (yr != "" or t == "Yes"):
            country = ""
            if (col.find("NA") != -1 or col.find("North America") != -1):
                country = "NA"
            elif (col.find("JP") != -1 or col.find("Japan") != -1):
                country = "JP"
            elif (col.find("Asia") != -1):
                country = "AS"
            elif (col.find("EU") != -1 or col.find("PAL") != -1 or col.find("Europe") != -1):
                country = "EU"
            elif (col.find("AU") != -1 or col.find("Australia") != -1):
                country = "AU"
            else:
                #print("unrecognized country: " + col)
                return (games, name)
            games[name][5] += country + ", "
            if (yr != ""):
                games[name][0] += yr + " " + country + " | "
    return (games, name)

def post_process(games, name, title):
    """add title to platforms data, remove trailing comma"""
    games[name][4] += title
    if (games[name][0] [-2:-1] == "|"):
        games[name][0] = games[name][0] [0:-3]
    if (games[name][5] [-2:-1] == ","):
        games[name][5] = games[name][5] [0:-2]
    return (games, name)

def write_db(games, name, f):
    """write games data of [name] to file, tab separated, if opened"""
    if (f):
        data = [name,] + [d if d != "" else "null" for d in games[name]]
        f.write("\t".join(data) + "\n")

def parse_name(games, name, title = ""):
    """parses game title for extra info: year, devs, regions"""
    year = ""
    dev = ""
    regions = ""
    group = m = ""
    while (group != None and m != None):
        m = re.search(r'(.+)\(([^\(\)]+)\)$', name) # [\w\s:-] [\w\d\s.,?:～]
        if (m):
            name = m.group(1).strip()
            group = m.group(2).strip()
            if (group):
                if (re.match(r'([A-Z]{2}\s*)+', group)):
                    regions = ", ".join(group.split())
                elif (re.match(r'[0-9]{4}', group)):
                    year = group
    if (name.rfind(" - ") != -1):
        dev = name[name.rfind("-") + 1 :].lstrip()
        name = name[: name.rfind("-") - 1].rstrip()
        
    games[name] = ["",] * 7
    games[name][0] = year
    games[name][2] = dev
    games[name][3] = dev
    games[name][4] = title
    games[name][5] = regions
    return (games, name)
    
def get_platforms(url):
    """get a list of elements w/ platform data from wiki url"""
    d = pq(url)
    c = d("div#mw-pages")("div.mw-content-ltr")
    return [l.find("a") for l in c("li")]

def mine_wiki_table(title, url, f = None):
    """mine wiki page with non-sortable table format"""
    print("parsing wiki table, non-sortable")
    d = pq(url)
    c = d("div#mw-content-text")
    tables = c("table.wikitable")
    if (len(tables) < 1):
        return None
    games = {}
    for table in tables:
        tr = table.getchildren()[0]
        header = str(table.getprevious().text_content())
        cols = [th.text for th in tr.getchildren()]
        if (len(cols) < 1):
            print("error getting columns for " + title)
            return {}
        print(title + " (" + header + ") cols: " + str(cols))
        for row in table.getchildren()[1 :]:
            name = ""
            tds = row.getchildren()
            # take 'rowspan' into account
            if (len(cols) != len(tds)):
                tds = [None,] * (len(cols) - len(tds)) + tds
            for td, col in zip(tds, cols):
                (games, name) = update_games(games, name, td, col)
            (games, name) = post_process(games, name, title)
            m = re.search(r'(\d{4}).*', header)
            if (m):
                games[name][0] = m.group(1).strip()
            write_db(games, name, f)
    return games

def mine_wiki_list(title, url, f = None):
    """mine wiki page with list format"""
    # http://en.wikipedia.org/wiki/List_of_Commodore_64_games_(A%E2%80%93M)
    print("parsing wiki list")
    d = pq(url)
    c = d("div#mw-content-text")
    games = {}
    head = ""
    for child in c.children():
        ul = None
        if (child.tag == "h2"):
            span = child.find("span")
            if ("id" in span.keys() and (span.attrib["id"] == "See_also" or \
                                         span.attrib["id"] == "External_links" or \
                                         span.attrib["id"] == "References")):
                return games
        elif (child.tag == "ul"):
            ul = child
        elif (child.tag == "dl"):
            ul = child
        elif (child.tag == "div"):
            if (child.find("ul") is not None):
                ul = child.find("ul")

        if (ul is not None):
            for li in ul.findall("li") or ul.findall("dt"):
                game = text(li)
                game.replace("\n", "")
                m = re.search(r'(\(.+\))', game)
                if (m):
                    game = game.replace(m.group(1), "")
                if (game != ""):
                    (games, name) = parse_name(games, game, title)
                    write_db(games, name, f)
                else:
                    print(text(li), text(li.getnext()))
    return games

def mine_wiki_err(title):
    # http://en.wikipedia.org/wiki/List_of_TecToy_Master_System_131_games
    print(title + " not in table or list format")
    return {}

def mine_wiki_page(title, url, f = None):
    """mine wiki page for list of video games, return dict of game info"""
    print("parsing wiki page")
    d = pq(url)
    tables = d("div#mw-content-text")("table.wikitable.sortable")
    if (len(tables) < 1):
        return mine_wiki_table(title, url, f) or mine_wiki_list(title, url, f) \
               or mine_wiki_err(title)
    games = {} # { name : (year, genre, dev, pub, platforms, regions, rating) }
    for table in tables:
        i = 0
        tr = table.getchildren()[i]
        header = str(table.getprevious().text_content()) \
                 if (table.getprevious() != None) else ""
        while (tr.tag != "tr"):
            tr = tr.getnext()
            i += 1
        cols = [text(th, no_sup = True) for th in tr.getchildren()]
        if (len(cols) < 1):
            print("error getting columns for: " + title + ", " + header)
            continue
        print(title + " (" + header + ") cols: " + str(cols))
        for row in table.getchildren()[i + 1 :]:
            name = ""
            for td, col in zip(row.getchildren(), cols):
                #print(col + " : " + text(td))
                (games, name) = update_games(games, name, td, col)
            (games, name) = post_process(games, name, title)
            write_db(games, name, f)

    if (title == "Sega arcade"):
        games.update(mine_wiki_list(title, url, f))
    
    return games

def mine_wiki(f = None, skip_to = None):
    """mine wikipedia list of all video games for info"""
    # games dict: { name : (year, genre, dev, pub, platforms, regions, rating) }
    pfs = get_platforms(wiki) + get_platforms(wiki2)
    titles = []
    games = {}
    for pf in pfs:
        title = pf.text

        # ignore combined pages, redundant pages
        if (title.find("Super Famicom and Super Nintendo") != -1):
            continue
        if (title.find("network") != -1 or title.find("multiplayer") != -1 or
            title.find("exclusive") != -1 or title.find("downloadable") != -1):
            continue
        if (title.find("CD-ROM") != -1 or title.find("DVD-9") != -1):
            continue
        if (title.find("arcade video games:") != -1):
            continue
        if (title.find("Gamesharing") != -1 or
            title.find("trackball") != -1 or
            title.find("System Link") != -1 or
            title.find("Move") != -1 or
            title.find("Games with Gold") != -1 or
            title.find("Xbox One applications") != -1):
            continue

        # strip prefix
        if (title.startswith("List of")):
            title = title.replace("List of", "").lstrip()
        elif (title.startswith("Index of")):
            title = title.replace("Index of", "").lstrip()
        elif (title.startswith("Draft")):
            continue        # empty page, ignore
        elif (title.startswith("Chronology")):
            continue        # redundant, ignore (Chronology of Wii games)
        else:
            #print("unknown prefix: " + title)
            # ignore kinect fun labs, platinum hits
            continue

        # remove parenthesis / colon for subcategories
        if (title.find(":") != -1):
            title = title[: title.find(":")]
        if (title.find(")") != -1):
            title = title[: title.find("(") - 1]

        # independent dreamcast games, other labels, etc
        title = title.replace("commercially released independently developed", "")
        title = title.replace("commercial", "")
        title = title.replace("free", "")
        title = title.replace("unlicensed and prototype", "")
        title.lstrip()

        # strip suffix
        if (title.endswith("video games")):
            title = title.replace("video games", "").rstrip()
        elif (title.endswith("games")):
            title = title.replace("games", "").rstrip()
        elif (title.endswith("titles")):
            title = title.replace("titles", "").rstrip()
        elif (title.endswith("software")):  # wii u software
            title = title.replace("software", "").rstrip()
        #elif (title.endswith("conversions")):
        #    title = title.replace("conversions", "").rstrip()
        elif (title.endswith("applications")):
            title = title.replace("applications", "").rstrip()
        elif (title.startswith("games compatible with")): # EyeToy (?)
            title = title.replace("games compatible with", "").lstrip()
        elif (title.startswith("games for the original")): # Game Boy
            title = title.replace("games for the original", "").lstrip()
        elif (title.startswith("Kinect games for")): # xbox 360 kinect games
            title = title.replace("Kinect games for", "").lstrip()
        elif (title.startswith("Xbox games on")): # xbox 360 kinect games
            title = title.replace("Xbox games on", "").lstrip()
        elif (title.find("Virtual Console games for") != -1):
            title = "Virtual Console"
        else:
            #print("unknown suffix: " + title)
            # ignore eye toy, exclusives, accessories, etc
            continue

        # find synonyms for game titles
        if title in synonyms:
            title = synonyms[title]

        if not title in titles:
            titles.append(title)

        if skip_to is not None and skip_to == title:
            skip_to = None

        if not skip_to:
            if (title == "arcade"):
                for sub in ["0..9",] + [chr(i) for i in range(65, 91)] + ["Not_released",]:
                    games.update(mine_wiki_page(title, wiki_base + pf.attrib['href'] + ":_" + sub, f))
            else:
                games.update(mine_wiki_page(title, wiki_base + pf.attrib['href'], f))
                
        f.write("\n\n\n")

    print(titles)
    return games

if __name__ == "__main__":
    f = open('games.txt', 'a', encoding = 'utf-8')
    #mine_wiki(f, skip_to = "TRS-80")
    f.close()
    pass

# http://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=List_of_ZX_Spectrum_games

# get rid of sup tags
# SNES - unlicensed games gives error, convert to sortable table?
# PC games - prints out table of A-Z
# Virtual console - first page doesn't work
# Magnavox games - bad formatting
# TurboGrafx-16 - irregular year numbers
# NES - SNES has bad date - year is duplicated (19941994 NA)
# GBC, Sega arcade has '' key
# Sega arcade not processed correctly, includes toc
# playstation region formatting odd
# iOS includes info at top
# xbox 360 - TB in year, fantasia?
# msdos - NAscar, bad formatting, all in one line, prints 0-9 A-Z info
# MXS - FRay, bad formatting
# EyeToy, Gizmondo, XBox - bad date, year is duplicated
# problem w/ parsing titles starting w/ NA, FR, ex - playstation NA
# incomplete entries - Oddworld: Stranger's Wrath on PS Vita
#    Dragon Warrior III by Square Enix on PC, Lego Movie TT Games/TT Fusion 3DS
#   Bubbliminate on Ouya, Action Man by 3DO Co on PS, LocoCycle on XBox One
#   Outfoxies on arcade, Hatoful on PC - no publisher
#   winds of thunder on Virtual Console, dev/pub not separated by \t

# scrap:
# m = re.match(r'([^\(\)\|]+).*?\(([^\(\)]*?)\)(.*)', value)
#    if m:
#        rest = release(m.group(3))
#        rest = " | " + rest if rest != "" else ""
#        return m.group(1).strip() + " (" + year(m.group(2)) + ")" + rest
#    else:
#        return year(value)
