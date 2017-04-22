## mine information from rf generation website ##

# import

from pyquery import PyQuery as pq
import urllib.request as urllib2
import re

# constants

rf_base = "http://rfgeneration.com"
rf_cgi  = rf_base + "/cgi-bin"
rf_list = rf_cgi  + "/collection.pl?name=&action=viewall&firstresult=%i&sort=COLLECTION&type=&searchname="

# global variables
related = {}

# functions

def reorder(text):
    """reorder strings that are in format [title, The] to [The title]"""
    m = re.match("(.+), The(.*)", text)
    return "The " + m.group(1) + m.group(2) if m else text

def find_alt(elem):
    """find alt text of images located somewhere within html element"""
    imgs = pq(elem)("img")
    return ", ".join([img.attrib["title"] for img in imgs if "title" in img.keys()])

def write_db(games, rfid, f):
    """write games data of [rfid] to file, tab separated, if opened"""
    # if file is given, not None, then write to file
    if (f):
        if (rfid != ""):
            # file contents are tab separated, and marked with null if unknown
            data = [d if d != "" else "null" for d in games[rfid]]
            f.write("\t".join(data) + "\n")
        else:
            print("empty name")

    # else, print out data for debugging
    else:
        data = [d if d != "" else "null" for d in games[rfid]]
        print("\t".join(data))

def try_pq(url, timeout = 10):
    """"keep try to download page, with given timeout"""
    while True:
        try:
            d = pq(url, timeout = timeout)
            return d
        except BaseException:
            print("retrying")

def mine_rf_game(url, f = None):
    """mine rf game page for info"""
    global related
    d = try_pq(url, timeout = 30)
    w = pq(d("table.windowbg2")[0])
    rfid = url[url.find("ID=") + 3 :]
    games = { rfid : ("",) * 8 }
    (title, year, genre, developer, publisher, console, regions, rating,
             players, member_rating) = ("",) * 10

    # find title
    title = w("tr#title")("div.headline").text()
    title = reorder(title)

    # find info paired with a label
    for tr in w("tr"):
        c = tr.getchildren()
        if (c is not None and len(c) >= 2):
            lower = c[0].text_content().lower()
            text  = c[1].text_content().strip().replace("\n", " ")
            if not(text == "----" or text == "-"):
                if "console:" in lower:
                    console += text
                elif "region:" in lower:
                    regions += find_alt(c[1]) + ", "
                elif "year:" in lower:
                    year = text + " " + regions.strip(", ")
                    year = year.strip()
                elif "developer:" in lower:
                    developer = text
                elif "publisher:" in lower:
                    publisher = text
                elif "rating:" in lower:
                    imgs = pq(c[1])("img")
                    rating += ", ".join([i.attrib['alt'] for i in imgs]) + " "
                    rating += text
                    rating = rating.strip()
                elif "sub-genre:" in lower:
                    genre += " | " + text
                    genre = genre.strip(" | ")
                elif "genre:" in lower:
                    genre = text
                elif "players:" in lower:
                    players = text

    # find regions released info
    for div in w("div.headline"):
        if "variations:" in div.text_content().lower():
            table = div.getnext().getnext()
            for wnd in pq(table)("tr.windowbg"):
                tds = wnd.findall("td")
                reg_td  = tds[1]
                rel_td  = tds[3]
                year_td = tds[5]
                alt = find_alt(reg_td)
                if alt != "" and not alt + ", " in regions:
                    regions += alt + ", "
                    year_text = year_td.text_content().strip()
                    if year_text != "----":
                        year += ", " + year_text + " " + alt
                        year = year.strip(", ")
                a = rel_td.find("a")
                if a is not None:
                    if (a.text_content().strip().lower() == title.lower()):
                        href = a.attrib['href']
                        rel_id = href[href.find("ID=") + 3 :]
                        related[rel_id] = True
                
    regions = regions.strip(", ").strip()

    # find member rating info
    td_rate = d("td#rate")
    if (td_rate != []):
        # overall rating is inside the largetext div
        large = td_rate.find("div.largetext")
        if large is not None:
            member_rating += large.text()

        # number of votes is inside the smalltext div
        small = td_rate.find("div.smalltext")
        if small is not None:
            member_rating += " " + small.text()
        member_rating = member_rating.strip()

    games[rfid] = (title, year, genre, developer, publisher,
                   console, regions, rating, players, member_rating)
    write_db(games, rfid, f)
    return games

def mine_rf_user(url, num, games = {}, f = None, skip_to = None):
    """mine rf user's collection list for info, return games dict"""
    global related
    num = num if num != -1 else 10
    url = url if "firstresult" in url else url + "&firstresult="
    for i in range(1, num, 50):
        d = try_pq(url + str(i), timeout = 30)
        for w in d("tr.windowbg") + d("tr.windowbg2"):
            tds = w.findall("td")
            [plat, r, shtype, title, publish, year, genre, q, b, m] \
                      = [td.text_content().strip() for td in tds][0 : 10]
            title = reorder(title)
            href = tds[3].find("a").attrib['href']
            m = re.match(".*ID=([0-9A-Z\-]*).*", href)
            assert m is not None, "error finding ID for: " + title
            rfid = m.group(1)

            if skip_to is not None and skip_to == title:
                skip_to = None
            
            if ("S" in shtype and rfid not in games and rfid not in related and \
                (title, plat, publish) not in games2 and skip_to == None):
                print("  mining game: " + title)
                games.update(mine_rf_game(rf_cgi + "/" + href, f))
                #games[rfid] = (title, year, genre, "", publish, plat, "", "")
    return games

def mine_rf(f = None, skip_to = (None, None)):
    """mine rf's video game collection list for info, returns games dict"""
    # games: { rfid : (title, year, genre, dev, pub,
    #                  platforms, regions, rating, players, member_rating) }
    games = {}
    (skip_to_user, skip_to_game) = skip_to
    for i in range(3251, 4700, 50):
        print("mining user data: " + str(i) + " to " + str(i + 50 - 1))
        d = try_pq(rf_list % (i), timeout = 30)
        for w in d("tr.windowbg") + d("tr.windowbg2"):
            tds = w.findall("td")
            name = tds[0].text_content().strip("\n\xa0")

            if skip_to_user != None and skip_to_user == name:
                skip_to_user = None

            if skip_to_user == None:
                for td in tds[1:]:
                    text = td.text_content().strip()
                    if "Collection" in text:
                        m = re.search(".*\((\d+)\).*", text)
                        num = int(m.group(1)) if m is not None else -1
                        link = td.find("div").find("a").attrib['href']
                        print(" mining user: " + name + " (" + str(num) + ")")
                        url = rf_base + link + "&firstresult="
                        games.update(mine_rf_user(url, num, games, f, skip_to_game))
                skip_to_game = None
    return games

def load(f = "games_rf.txt"):
    """load games dict from file, return games info as dict"""
    f = open(f, 'r', encoding = 'utf-8')
    games2 = {}
    for line in f.readlines():
        line = line.strip().strip("\r\n")
        # ignore blank lines
        if len(line) < 0:
            continue

        # ignore comments
        elif line.startswith("# "):
            continue

        info = line.split("\t")
        if len(info) == 10:
            (name, year, genre, dev, pub, plat, area, rate, players, mem_rate) \
                   = info
            if (name, plat, pub) not in games2:
                games2[(name, plat, pub)] = \
                              (year, genre, dev, area, rate, players, mem_rate)
    return games2

def load_rel(f = "related.txt"):
    """load related games data from file, return related info as dict"""
    f = open(f, 'r')
    related = {}
    for line in f.readlines():
        line = line.strip()
        # ignore blank lines
        if len(line) < 0:
            continue

        related[line] = True
    return related

if __name__ == "__main__":
    f = open('games_rf.txt', 'a', encoding = 'utf-8')
    related = load_rel()
    games2 = load()
    games = mine_rf(f, skip_to = ("Dijago", None))
    f.close()

# TODO - use Twisted? (https://twistedmatrix.com/trac/)
