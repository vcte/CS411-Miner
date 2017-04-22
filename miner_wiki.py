## mine information from wikipedia info table ##

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

genres = ["educational", "adventure", "golf", "shogi", "role-playing", "open-world", "shooter", "trading",
          "visual novel", "puzzle", "shoot -em up", "shoot em up", "racing", "maze", "card", "tennis", "strategy",
          "football", "sports", "interactive fiction", "action", "platform", "stealth", "chess", "pinball"]

# functions

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
    f = open('games_wiki.txt', 'a', encoding = 'utf-8')
    #mine_wiki(f, skip_to = "TRS-80")
    f.close()
    pass

# prob - Platinum_Games in Wii section
