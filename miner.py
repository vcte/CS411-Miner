## mine information from wiki pages ##

# import

from pyquery import PyQuery as pq
import urllib.request as urllib2
import html.parser
from math import log
import re

import queue
from threading import Thread, Lock

# constants

wiki_base = "http://en.wikipedia.org"
wiki = wiki_base + "/wiki/Category:Video_game_lists_by_platform"
wiki2 = wiki_base + "/w/index.php?title=Category:Video_game_lists_by_platform&pagefrom=Windows%0AIndex+of+Windows+games+%28P%29#mw-pages"
api_base = wiki_base + "/w/api.php?action=query&prop=revisions&rvprop=content&format=json&titles="

synonyms = { "3DO Interactive Multiplayer" : "3DO",  "Enix home computer" : "Enix",
             "Nintendo Entertainment System" : "NES", "Super Nintendo Entertainment System" : "SNES",
             "Nintendo GameCube" : "GameCube", 
             "PC Engine CD" : "TurboGrafx-16", "PC Engine" : "TurboGrafx-16", "Windows" : "PC",
             "Microsoft Windows" : "PC",
             "Windows Mobile Professional" : "Pocket PC", "PlayStation Portable" : "PSP",
             "PlayStation 2" : "PS2", "PlayStation 3" : "PS3", "PlayStation 4" : "PS4",
             "Macintosh" : "Mac", "PlayStation Vita" : "Vita", "Apple ][" : "Apple II" }

genres = ["educational", "adventure", "golf", "shogi", "role-playing", "open-world", "shooter", "trading",
          "visual novel", "puzzle", "shoot -em up", "shoot em up", "racing", "maze", "card", "tennis", "strategy",
          "football", "sports", "interactive fiction", "action", "platform", "stealth", "chess", "pinball"]

# functions

def unwiki(text, quiet = True):
    """convert text in wiki markup format, into plain text"""
    # remove full html comments
    while ("<!--" in text and "-->" in text):
        text = text[: text.find("<!--")] + text[text.find("-->") + 3 :]
        quiet or print("-html: \t" + text)

    # remove tags, but keep inner contents
    tags = ["sup", "small", "s", "center", "u", "strong", "nowiki"]
    for tag in tags:
        bgn = "<" + tag + ">"
        end = "</" + tag + ">"
        if (bgn in text and end in text):
            text = text.replace(bgn, " ").replace(end, " ")
    
    # remove tags
    tags = ["ref", "br", "Br", "span", "sup", "small", "center", "s", "div", "u", "strong", "nowiki"]
    tags = tags + list(map(lambda s: s.upper(), tags))
    for tag in tags:
        while "<" + tag in text:
            # find first instance of tag w/o another tag inside of it
            opn = -1
            while (True):
                # use sorted instead of list to get first match appearing in string
                opn  = text.find("<" + tag, opn + 1)
                end  = (list(map(lambda s: text.find(s, opn + 1) + len(s), filter(lambda s: s in text,
                            ["</" + tag + ">", tag + ">", "/>", ">"]))))[0]

                # if same tag is found within the contents of the tag, then try again, otherwise break
                if not "<" + tag in text[opn + 1 : end]:
                    break
            orig = text
            text = text.replace(text[opn : end], "" if tag != "br" else "\n")

            # if no change, then try another tag, return to this tag later
            if (orig == text):
                tags.append(tag)
                break

    # remove standalone tags
    for tag in tags:
        text = text.replace("</" + tag + ">", "")

    if ("<" in text and ">" in text):
        print("unknown tag? " + text[text.find("<") : text.find(">") + 1])
            
    quiet or print("-tag: \t" + text)
        
    # remove style attributes
    styles = ["style", "width", "scope", "rowspan", "colspan", "class", "align"]
    for style in styles:
        if " " + style + "=" in text:
            ind = text.find(style)
            end = text.find("|", ind)
            text = text.replace(text[ind : end + 1], "") if end != -1 else \
                   text.replace(text[ind :], "")
    quiet or print("-style: \t" + text)

    # balance template brackets
    if balanceof(text) != 0:
        text += "}}" * (balanceof(text))
    
    # remove templates
    temps = ["Anchor", "Citation needed"]
    for temp in temps:
        if temp in text and "{{" in text and "}}" in text:
            ind = text.find(temp)
            text = text.replace(text[text.rfind("{{", 0, ind) :
                                     text.find("}}", ind) + 2], "")
    quiet or print("-temp: \t" + text)

    # remove link targets
    while ("[[" in text and "|" in text and "]]" in text):
        # find first "|" bar inside of "[[" "]]" brackets
        ind = lnk = end = -1
        while (lnk == -1 or end == -1):
            ind = text.find("|", ind + 1)
            lnk = text.rfind("[[", text.rfind("]]", 0, ind) + 1, ind)
            end = text.find("]]", ind)

            # end if no more "|" bar characters
            if (ind == -1):
                break
        if (ind == -1):
            break

        # regular target link, so remove target
        if (not text[ind : ind + 3] == "|]]"):
            text = text[: lnk ] + text[ind + 1 : end] + text[end + 2 :]

        # automatic target link
        else:
            # remove text in parentheses
            if (text.rfind("(", 0, ind) != -1):
                text = text[: text.rfind("(", 0, ind)].strip() + \
                       text[text.rfind(")", 0, ind) + 1 :].strip()

            # remove text after comma
            if (text.rfind(",", 0, ind) != -1):
                text = text[: text.rfind(",", 0, ind)].strip() + \
                       text[ind + 1 :].strip()

            # remove "Wikipedia:" marker
            if (("Wikipedia:") in text):
                text = text.replace("Wikipedia:", "")
            text = text[: ind] + text[ind + 1 :]
    quiet or print("-target: \t" + text)
    
    # remove links
    while (("[[") in text and ("]]") in text):
        text = text.replace("[[", "").replace("]]", "")
        quiet or print("-link: \t" + text)

    # remove link with single bracket
    while (("[") in text and ("]") in text and ("http") in text):
        m = re.search("(.*)\[http[^\s\[\]]+\s+([^\[\]]+)\](.*)", text, re.DOTALL | re.I)
        m2 = re.search("(.*)\[http[^\s\[\]]+\](.*)", text, re.DOTALL | re.I)
        if (m):
            text = "".join(m.groups())
        elif (m2):
            text = "".join(m2.groups())
        else:
            break
        quiet or print("-bracket: \t" + text)
        
    # replace misc templates - vgy, Nihongo, date, color, flagicon, excl, etc
    regexes = [('', r'[V|v]gy\s*\|\|?(\d{4})(?:\|\d{4})?'),
               ('', r'[V|v]gy\s*\|[T|t][B|b][A|a]'),
               ('', r'[N|n]ihongo\s*\|([^\{\}]*?)\|[^\{\}]*'),
               (' ', r'[D|d]ts\s*\|(\d{4}.\d{1,2}.?\d{1,2}?)'),
               (' ', r'[D|d]ts\s*\|([\w\s\d,-| ]*)'),
               ('', r'[D|d]ate\s*\|([\w\d\s-]+)\|?.*?'),
               ('', r'[C|c]olor\s*\|[^\{\}]*?\|([^\{\}]*)'),
               ('', r'[F|f]lagicon\s*\|([^\}]+)'),
               ('', r'[N|n]owrap\s*\|+([^\{\}]*?)'),
               ('', r'[S|s]mall\s*\|([^\{\}]*?)'),
               ('', r'[S|s]up\s*\|([^\{\}]*?)'),
               ('', r'[N|n]oitalic\s*\|([^\{\}]*?)'),
               ('', r'[S|s]c\|([^\{\}]*?)'),
               ('', r'([Y|y]es|[N|n]o|[P|p]artial|[M|m]aybe|dunno|Y|N|y|n)(?:\|[^\{\}]*)?'),
               ('', r'(Cancelled)\|?[^\{\}]*?'),
               ('', r'[S|s]ort\|[^\{\}\|]*?\|([^\{\}]*)'),
               ('', r'(?:[C|c]itation [N|n]eeded|[C|c]n)(?:.?span)?(?:\|[^\{\}]*?)?'),
               ('', r'[C|c]ite[^\{\}]*?'),
               ('', r'[R|r]ef[^\|]*?\|[^\{\}]*?(?:\|[^\{\}]*)?'),
               ('', r'[R|r]efn\|[^\{\}]+?'),
               ('', r'[D|d][i|n][s]?[^\{\}]*?'),
               ('', r'[S|s]fn\s*\|[^\{\}]*?'),
               ('', r'[E|e]fn\s*\|[^\{\}]*?'),
               ('', r'((?:[N|n]/?[A|a])|(?:[T|t][B|b][A|a])[^\{\}]*?)'),
               ('', r'(?:AUS|BRA|CAN|GER|ESP|EU|FIN|FRA|JPN|UK|USA)'),
               (' ', r'(AUS|US|UK|EU|JP)\|([^\{\}]*?)'),
               ('', r'#time:[^\{\}]*?,\s*.\|([\w\d\s-]*)'),
               (' ', r'[R|r]elease date and age\s*\|(\d*)\|?(\d*)\|?(\d*)[^\{\}]*?'),
               (' ', r'[S|s]tart date and age\s*\|(\d*)\|?(\d*)\|?(\d*)[^\{\}]*?'),
               (' ', r'[S|s]tart.?[D|d]ate\|?(\d*)\|?(\d*)\|?(\d*)[^\{\}]*?'),
               (' ', r'[E|e]nd [D|d]ate\s*\|(\d*)\|?(\d*)\|?(\d*)[^\{\}]*?'),
               ('', r'[V|v]grelease new\|([^\{\}v]*)\|v=\d\|([^\{\}]*)'),
               #(' ', r'[V|v](?:grelease|ideo game release)\s*new\s*\|+(?:v=\d\|)?' + r'(\w*)\|?([^\{\}\|]*)(\|{0,1})' * 6),
               (' ', r'[V|v](?:grelease|ideo game release)\s*(?:new)?\s*\|{0,2}(?:v=\d\|)?'+'([^=\|\}]*)(?:=|\|)([^=\|\}]*)'),
               (' ', r'[V|v](?:grelease|ideo game release)\s*(?:new)?\s*\|{0,2}(?:v=\d\|)?'+'([^=\|\}]*)(?:=|\|)([^=\|\}]*)(\|{0,2})' * 2),
               (' ', r'[V|v](?:grelease|ideo game release)\s*(?:new)?\s*\|{0,2}(?:v=\d\|)?'+'([^=\|\}]*)(?:=|\|)([^=\|\}]*)(\|{0,2})' * 3),
               (' ', r'[V|v](?:grelease|ideo game release)\s*(?:new)?\s*\|{0,2}(?:v=\d\|)?'+'([^=\|\}]*)(?:=|\|)([^=\|\}]*)(\|{0,2})' * 4),
               (' ', r'[V|v](?:grelease|ideo game release)\s*(?:new)?\s*\|{0,2}(?:v=\d\|)?'+'([^=\|\}]*)(?:=|\|)([^=\|\}]*)(\|{0,2})' * 5),
               (' ', r'[V|v](?:grelease|ideo game release)\s*(?:new)?\s*\|{0,2}(?:v=\d\|)?'+'([^=\|\}]*)(?:=|\|)([^=\|\}]*)(\|{0,2})' * 6),
               ('', r'[V|v]grtbl(?:-tx|-bl)?\|?([^\{\}]*?)'),
               (' ', r'[V|v](?:grelease|ideo game release\*)\|'),
               (' ', r'[V|v](?:grelease|ideo game release\s*)\|{1,2}([^=\{\}]*)(=?)([^=\{\}]*?)'),
               (' ', r'[V|v](?:grelease|ideo game release)\s*(?:new)?\|{1,2}([^\|]+?)\|([^\{\}]+)'),
               ('', r'[V|v](?:g|ideo game).?rating[s]?\|([^\{\}]*?)'),
               ('', r'(?:[O|o]fficial\s)?[W|w]eb(?:[S|s]ite)?\s*\|?([^\{\}]+)'),
               ('', r'(?:[D|d]ecrease|[I|i]ncrease|[L|l]oss)'),
               ('', r'([U|u][S|s]\$?\|?[^\{\}]+)'),
               ('', r'([Y|y][E|e][N|n]\|?[^\{\}]+)'),
               ('', r'([J|j][P|p][Y|y]\|?[^\{\}]+)'),
               ('', r'([S|s][E|e][K|k]\|?[^\{\}]+)'),
               ('', r'([T|t][Y|y][O|o]\|?[^\{\}]+)'),
               ('', r'([C|c][N|n][Y|y]\|?[^\{\}]+)'),
               ('', r'((?:[J|j]asdaq|[H|h]kex)\|?[^\{\}]+)'),
               ('', r'(€\|?[^\{\}]+)'),
               ('', r'[F|f]ormat.?[N|n]um[^\{\}]*'),
               ('', r'[C|c]ollapsible[^\|\{\}]*\|(?:\s*framestyle[^\|]*?\|)?\s*(?:title\s*=\s*)?(?:([^\|]*?\d[^\|]*?)|(?:[^\|]*()[^\|]+))[\| ]*(?:\s*titlestyle[^\|]*?\|)?' + r'(?:\d=)*([^\{\}]*\|?)' * 4),
               ('', r'[F|f]lat[ ]?[L|l]ist\|([^\{\}]+)'),
               ('', r'[U|u]bl\|((?:[^\|\{\}]+\|{0,3})+)'),
               ('', r'[U|u]nbulleted\s[L|l]ist([^\{\}]*?)'),
               ('', r'[H|h]list\s*\|([^\{\}]+?)'),
               ('', r'[U|u][R|r][L|l]\s*\|?([^\{\}]+?)(?:\s*\|\s*[^\{\}]+)?'),
               ('', r'([C|c]heck[ ]?[M|m]ark)\|[^\{\}]*?'),
               ('', r'([C|c]ross)\|[^\{\}]*?'),
               ('', r'[P|p]lain.?list\s*\|([^\{\}]*?)\s*'),
               ('', r'[T|t]ooltip\s*\|(.*)(?:\|[^\{\}]*?)?'),
               ('', r'[A|a]bbr\|([^\{\}]*?)'),
               ('', r'(.)'),
               ('', r'[N|n]ot a typo\|([^\{\}]*?)'),
               ('', r'[U|u]nknown'),
               ('', r'[R|r]eflist'),
               ('', r'[V|v]ideo game lists by platform')]

    for regex in regexes:
        r = re.compile(r'(.*)\{\{\s*' + regex[1] + '\s*\}\}(.*)', re.DOTALL | re.I)

        # remove all occurences of template
        while (re.match(r, text)):
            m = re.match(r, text)
            delim = regex[0]
            text = delim.join([g for g in m.groups() if g is not None])
            quiet or print("-regex: \t" + text)

    # expand cpu spec template
    cpus = ['Z80', 'z80', '6502', 'POKEY']
    for cpu in cpus:
        r = re.compile(r'(.*)\{\{' + cpu + r'\|?([^\{\}\|]*?)' * 2 + r'\}\}(.*)')
        while (re.match(r, text)):
            m = re.match(r, text)
            text = m.group(1) + " " + m.group(2) + "x " + cpu + " @ " + m.group(3) + " MHz" + m.group(4)

    # expand raster details template
    rasters = ['Raster', 'raster']
    for raster in rasters:
        r = re.compile(r'(.*)\{\{' + raster + r'\|rgb\s*=\s*(\d+)\|vertical\s*=\s*(\d+)\|size\s*=\s*(\d+)\}\}(.*)')
        while (re.match(r, text)):
            m = re.match(r, text)
            text = m.group(1) + " " + "RGB raster, vertical orientation (" + m.group(4) + "-inch diagonal)" + m.group(5)

    # replace fraction templates
    fracs = [(r'frac\|1\|4', "¼"), (r'frac\|1\|2', "½"), (r'frac\|3\|4', "¾"),
             (r'frac\|3\|1\|2', "3½")]
    for frac in fracs:
        text = re.sub(r'\{\{' + frac[0] + r'\}\}', frac[1], text)

    # clean numerical lists
    r = re.compile(r'(.*)(\|)\s*\d{1,2}\s*=(.*)(\||\}|$)(.*)', re.DOTALL | re.I)
    while (re.match(r, text)):
        m = re.match(r, text)
        text = "".join(m.groups())

    # remove all unknown templates
    while ("}}" in text and "{{" in text):
        temp = text[text.find("{{") : text.find("}}") + 2]
        text = text.replace(temp, "")
        print("unknown template? " + temp)
        if temp == "":
            break

    # remove partial html comments
    while ("<!--" in text or "-->" in text):
        text = (text[: text.find("<!--")]    if "<!--" in text else "") + \
               (text[text.find("-->") + 3 :] if "-->" in text else "")
        quiet or print("-html: \t" + text)

    # remove italics, bold
    if ("''" in text or "\\'\\'" in text):
        text = text.replace("'''", "").replace("''", "") \
                   .replace("\\'" * 3, "").replace("\\'" * 2, "")
    quiet or print("-italic: \t" + text)

    # convert escape characters and unicode characters
    text = convert(text)
    quiet or print("-escape: \t" + text)
    
    # combine multiple lines, using bar character
    text = " | " .join(t.strip() for t in text.splitlines() if t.strip() != "") \
           if text != "" else ""
    quiet or print("-lines: \t" + text)
    
    # reorder text if in "xxx, The yyy" format
    text = reorder(text)
    quiet or print("-reorder: \t" + text)

    # eliminate redundant spacing
    text = re.sub(r'\s+', " ", text)

    # eliminate irregular characters
    text = text.replace("•", "")
    
    return text.strip()

def convert(text):
    """convert escape characters and unicode characters and html symbols"""
    # convert all known unicode / escape chars
    while ("\\" in text):
        ind = text.find("\\")
        if ind < 0 or ind + 1 >= len(text):
            break
        if (text[ind + 1] == "n"):
            text = text.replace("\\n", "\n")
        if (text[ind + 1] == "t"):
            text = text.replace("\\t", " ")
        elif (text[ind + 1] == "u"):
            code = text[ind + 2 : ind + 6]
            text = text.replace("\\u" + code, chr(int(code, 16)))
        elif (text[ind + 1] == "'"):
            text = text.replace("\\'", "\'")
        elif (text[ind + 1] == "\""):
            text = text.replace("\\\"", "\"")
        elif (text[ind + 1] == "\\"):
            text = text.replace("\\\\", "\\")
        elif (text[ind + 1] == "}"):
            text = text.replace("{{\\}}", "/")
        elif (text[ind + 1] == "\\"):
            text = text.replace("\\b", "\b")
        else:
            print("convert error: " + text[ind + 1])
            #raise BaseException
            break

    # convert html symbols
    text = html.parser.HTMLParser().unescape(text)
    text = text.replace("&ndash;", "–")
    text = text.replace("&mdash;", "—")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    text = text.replace("&times;", "×")
    text = text.replace("&copy", "©")
    text = text.replace("&nbsp;", "\n")
        
    return text

def reorder(text):
    """reorder strings that are in format [title, The] to [The title]"""
    m = re.match("(.+)(?:,|;) The(.*)", text)
    return "The " + m.group(1) + m.group(2) if m else text

def balanceof(text):
    """find bracket balance of string, return 0 if balanced, else diff in brackets"""
    return text.count("{{") - text.count("}}")

def bar_split(text):
    """split text divided by wiki formatted bars, into list of strings"""
    text = re.sub(r'(\{\{[^\{\}]+)\|\|([^\{\}]+)', r'\1|\2', text)
    strs = []
    while (True):
        # use non-greedy matching to find first bar separator, from the left
        m = re.search(r'(.+?)([\|]{2,})(.+)', text)
        if (m is None):
            # if no bar separator found, then return w/ remaining text
            strs.append(text.strip())
            return strs
        else:
            # split up text
            strs.append(m.group(1).strip())
            bars = m.group(2)
            text = m.group(3)

            # append blank entries, if multiple bar separators (ex: abc |||| def)
            lenb = len(bars) // 3 - 1 if (len(bars) % 3 == 0) else \
                   len(bars) // 2 - 1 if (len(bars) % 2 == 0) else 0
            strs += [""] * lenb            

def get_mo(text):
    """take string representing month or abbreviation, convert it to number"""
    mo = { "january" : "1", "february" : "2", "march" : "3", "april" : "4", "may" : "5", "june" : "6",
           "july" : "7", "august" : "8", "september" : "9", "october" : "10", "november" : "11", "december" : "12",
           "jan" : "1", "feb" : "2", "mar" : "3", "apr" : "4", "jun" : "6", "jul" : "7", "aug" : "8",
           "sep" : "9", "sept" : "9", "oct" : "10", "nov" : "11", "dec" : "12" }
    return mo.get(text.lower().strip("."), "UNK")

def year(text, multiline = True):
    """interpret date data, convert to mm/dd/yyyy format"""
    # if multiple lines given, then find year for each line
    if (len(text.splitlines()) > 1 and multiline):
        return " | ".join([year(t) for t in text.splitlines() if t != ""])
    if (len(text.split("|")) > 1): # " | "
        return " | ".join([year(t) for t in text.split("|") if year(t) != ""])

    # extract region information
    regions = re.search(r"(([A-Z]{2,3}([ ]?(,|/)[ ]?)?)+)", text)
    reg_str = " " + regions.group(1) if regions else ""

    # search for date in format: 10/21/2003
    date0 = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if (date0):
        return date0.group(1) + "/" + date0.group(2) + "/" + date0.group(3) + reg_str

    # search for date in format: 2003/10/21
    date0a = re.search(r"(\(d{4})/(\d{1,2})/(\d{1,2})", text)
    if (date0a):
        return date0a.group(2) + "/" + date0a.group(3) + "/" + date0a.group(1) + reg_str

    # search for date in format: October 21, 2003
    date1 = re.search(r"([A-Z|a-z|\.]+) (\d{1,2})(?:th)?.? (\d{4})", text)
    if (date1):
        return get_mo(date1.group(1)) + "/" + date1.group(2) + "/" + date1.group(3) + reg_str

    # search for date in format: 2003-10-21
    date2 = re.search(r"(\d{4})[^\d](\d{1,2})[^\d](\d{1,2})", text)
    if (date2):
        return date2.group(2) + "/" + date2.group(3) + "/" + date2.group(1) + reg_str
    
    # search for date in format: 21 October 2003
    date1b = re.search(r"(\d+) ([A-Z|a-z|\.]+) (\d+)", text)
    if (date1b):
        return get_mo(date1b.group(2)) + "/" + date1b.group(1) + "/" + date1b.group(3) + reg_str

    # search for date in format: October 2003
    date1a = re.search(r"([A-Z|a-z|\.]+)\s+([1|2]\d{3})", text)
    if (date1a):
        return date1a.group(2) + reg_str

    # search for date in format: 2003
    date3 = re.search(r"([1|2]\d{3})", text)
    if (date3):
        return date3.group(1) + reg_str

    # search for date in format: 10/14/03
    date4 = re.search(r"(\d{2})[^\d](\d{2})[^\d](\d{2})", text)
    if (date4):
        yr = date4.group(3)
        yr = "19" + yr if int(yr) >= 50 else "20" + yr
        return date4.group(1) + "/" + date4.group(2) + "/" + yr

    # search for 'TBA' string
    tba = re.search(r"[T|t][B|b][A|a]", text)
    if (tba):
        # don't repeat the string 'TBA' 
        reg_str = re.sub(r'\s*[T|t][B|b][A|a]\s*', '', reg_str)
        return "TBA" + reg_str

    # search for 'TBD' string
    tbd = re.search(r"[T|t][B|b][D|d]", text)
    if (tbd):
        # don't repeat the string 'TBD' 
        reg_str = re.sub(r'\s*[T|t][B|b][D|d]\s*', '', reg_str)
        return "TBD" + reg_str

    # if date not parsed, then return empty string
    return ""

def country(text):
    """find country that text is referring to"""
    if   (("NA") in text or ("North America") in text):
        return "NA"
    elif (("JP") in text or ("Japan") in text):
        return "JP"
    elif (("AS") in text or ("Asia") in text):
        return "AS"
    elif (("EU") in text or ("Europe") in text):
        return "EU"
    elif (("CA") in text or ("Canada") in text):
        return "CA"
    elif (("PAL") in text):
        return "PAL"
    elif (("FR") in text or ("France") in text):
        return "FR"
    elif (("DE") in text or ("Ger") == text):
        return "DE"
    elif (("AU") in text or ("Australia") in text or ("Australasia") in text):
        return "AU"
    elif (("BR") in text or ("Brazil") in text):
        return "BR"
    elif (("SK") in text or ("South Korea") in text):
        return "SK"
    elif (("WW") in text or ("World") in text):
        return "WW"
    elif (("INT") in text or ("International") in text):
        return "INT"
    else:
        return ""

def to_canon(text, dev = True, quiet = True):
    """find simplest string representing the developer"""
    sufs = ["ltd", "inc", "llc", "pty", "ab", "studios", "studio", "multimedia",
            "media", "entertainment", "international", "corporation", "corp", "co",
            "software", "soft", "games", "productions", "production", "company",
            "international", "int", "foundation", "interactive", "group",
            "publishing", "limited", "digital", "design", "invention", "wireless"]
    spcs = [('á', 'a'), ('ä', 'a'), ('é', 'e'), ('ë', 'e'), ('ı', 'i'), ('ï', 'i'),
            ('ø', 'o'), ('ō', 'o'), ('õ', 'o'), ('ó', 'o'), ('ü', 'u'), ('ú', 'u'),
            ('ū', 'u'), ('ç', 'c'), ('ł', 'l'), ('ñ', 'n'), ('ş', 's'),
            ('&', 'and')]
    
    # convert to lowercase, remove punctuation
    canon = re.sub(r'[,/\.]', "", text.strip(" \r\n\t").lower())
    quiet or print(canon)

    # remove parenthesized text, if enough information left
    m = re.match(r'(.*)\s*\([^\(\)]*?\)(.*)', canon)
    if m:
        rem = "".join(m.groups())
        if len(rem) > log(len(canon) - len(rem)):
            canon = rem
    quiet or print(canon)

    # convert special characters
    for char, norm in spcs:
        canon = canon.replace(char, norm)
    quiet or print(canon)

    # remove all remaining non alphanumerical characters, if enough info
    if len(canon) > 4:
        canon = re.sub(r'[^0-9A-Za-z ]', '', canon)
    quiet or print(canon)

    # remove suffixes
    if (dev):
        for suf in sufs:
            m = re.match(r'(.*?)\s+' + suf + r'$', canon)
            if m:
                rem = m.group(1)
                # only remove suffix if 'rem' holds enough info, relative to 'suf'
                if len(rem) > log(len(suf), 2):
                    canon = rem
    quiet or print(canon)

    # remove 'the'
    canon = re.sub(r'^[T|t]he ', '', canon).strip()

    # make all plural objects singular
    if (dev):
        canon = re.sub(r'([0-9A-Za-z]+)s(?:\s|$)', r'\1', canon)

    # remove spaces
    canon = re.sub(r' ', '', canon)
    
    return canon

def split_bal(text, r = r'\n|, |;|/|\|'):
    """split up text, so that parentheses are balanced, strips text of whitespace"""
    texts = re.split(r'(' + r + r')', text)
    i = 0
    while i < len(texts):
        while texts[i].count("(") != texts[i].count(")"):
            if i + 1 >= len(texts):
                break
            texts[i : i + 2] = [texts[i] + texts[i + 1]]
        i += 1
    texts = [t.strip(" \t\n\r") for t in texts if not re.match(r, t)]
    return texts
    
def find_devs(text):
    """parse list of developers in delimeter separated text, return official names separated by bar"""
    text = re.sub(r', [I|i]nc', ' Inc', text)
    text = re.sub(r', [L|l][L|l][C|c]', ' LLC', text)
    #text = text.replace("}}", "}}|").replace("{{", "|{{")
    return " | ".join( \
                    [find_dev(clean_dev(t.strip(" \t\n\r"))) for t in
                 split_bal(text, r = r', |\n|/|\|') if #r'\n|,|/|\|
                 re.match(r'^\s+$', t) is None and t != ""])

def find_dev(text):
    """try to find developer from list of developers"""
    # preserve content in parenthesis, if any
    m = re.search(r'(\([^\(\)]*?\))', text)
    appd = " " + m.group(1) if m else ""

    # find smallest, canonical representation of given text
    canon = to_canon(text)
    if canon in devs:
        # found match with developer / publisher in database
        return devs[canon] + appd
    else:
        #print("no match for: " + text.strip())
        return text.strip()

def clean_dev(text):
    """clean developer text, using specific rules"""
    text = text.replace("Additional work by:", "")
    return text

def get_devs():
    """get all developers, in dict format: { canonical_name : full_name }"""
    devs = {}
    faq = open('dev_faq.txt', 'r', encoding = 'utf-8')
    for line in faq.readlines():
        line = line.strip()
        [canon, dev,] = line.split("\t")
        if not canon in devs:
            devs[canon] = dev
    return devs

def isTitle(low, dat):
    """return true if column is for video game titles, and name is not blank"""
    return ((low.find("title") != -1 or low.find("name") != -1 or
             low.find("game") != -1) and dat != "—")

def isDev(low):
    """returns true if column is for video game developers"""
    return low.find("develop") != -1 or low.find("program") != -1

def isPub(low):
    """returns true if column is for video game publishers"""
    return low.find("publish") != -1

def get_file(value):
    """extract link to file, from wiki text"""
    beg = value.find("[[") + 2 if "[[" in value else 0
    end = value.find("|") if "|" in value else value.find("]]")
    end = len(value) if end == -1 else end
    return value[beg : end].strip(" \t\r\n").replace(" ", "_")

def find_consoles(value):
    """find synonyms for all consoles in delimeter separated text"""
    return " | ".join([synonyms[cons.strip()] if cons.strip() in synonyms else cons.strip()
                       for cons in re.split(r', |;|/|\|', value)
                       if cons.strip() != ""])

def separate(value):
    """separate text using bar, instead of comma or slash"""
    return " | ".join([v.strip()
                       for v in split_bal(value, r', |;|/|\|') #r',|;|/|\|'
                       if v.strip() != ""])

def preproc_space(text):
    """line preprocessing - removes first space"""
    return text.replace(" ", "", 1) if text.startswith(" ") else text

def preproc_star(text):
    """line preprocessing - removes first asterisk"""
    return text.replace("*", " |", 1) if text.startswith("*") else text

def preproc(text):
    """line preprocessing - removes first space, removes first asterisk"""
    return preproc_star(preproc_space(text))

def release(value, quiet = True):
    """interpret release date in wiki text"""
    value = value.replace("</ref>''", "</ref>|''")          # fix for minecraft
    value = unwiki(value.replace("}}", "}}|").replace("{{", "|{{"), quiet)
    value = re.sub(r'([^ ])\|([^ ])', r'\1 | \2', value)
    if re.match(r'^[\d\|]+\s*\-\s*[\d\|]+$', value):
        return "-".join([year(v) for v in value.split("-")])
    if re.match(r'^([\w\s]+-[\d\s]+\|?)+$', value):
        value = value.replace("-", "|")
    out = ""
    values = [v for v in value.split("|") if not re.match(r'^[\s,;/]+$', v) and v != '']
    for val, i in zip(values, range(len(values))):
        yr = year(val)
        if yr != "":
            par = " " + val[val.find("(") : val.find(")") + 1] if "(" in val and ")" in val else ""
            par = par.replace("(", "[").replace(")", "]")
            out += yr + par + " | "
        else:
            out = out.strip(" | ") + ") | " if out.count("(") > out.count(")") else out
            val = val.strip().replace("(", "[").replace(")", "]")
            val = synonyms.get(val, val)
            out += val
            out += " (" if i != len(values) - 1 else ""
        quiet or print(out)
            
    out = out.strip("| (")
    out += ")" if out.count("(") > out.count(")") else ""
    #out = re.sub(r'\s*\(\s*\)\s*', ' ', out)
    out = re.sub(r'(^|\|)[^\(\)\|]*\(\)[^\(\)\|]*\|', r'\1', out)
    return out.strip(" \t\n\r")

def find_wiki_url(text):
    """find first link in wiki markup text, return link and name"""
    link = text[text.find("[[") + 2 : text.find("]]")]
    link = link[: link.find("|")] if "|" in link else link
    link = link.replace("Wikipedia:", "")
    name = unwiki(text[text.find("[[") : text.find("]]") + 2]) #name = link 
    link = link.replace(" ", "_")
    link = convert(link)
    return (link, name)

def open_wiki_url(dat, f = None, games = {}, skip_to_game = None):
    # find first wikipedia link, contained in dat, write to file, return result as dict
    if "[[" not in dat and "]]" not in dat:
        return {}

    # find link in wiki markup text
    (link, name) = find_wiki_url(dat)

    # if skipping, and desired title is not reached, then return w/ empty dict
    if skip_to_game is not None and skip_to_game == name:
        skip_to_game = None
    if skip_to_game:
        return {}

    # if games dict already has the game, then return w/ empty dict
    if name in games:
        return {}

    # update games dict, with data from infobox
    games.update(mine_wiki_info(name, link, f = f))

    return games

def update_games(games, name, dat, col):
    """update games info with new data, return games and name"""
    low = col.lower()
    if (name == ""):
        # set the name of game, add a new blank entry to games dictionary
        if isTitle(low, dat):
            name = reorder(dat)
            (games, name) = parse_name(games, name)
    else:
        t = dat
        yr = year(t)
        cn = country(col)

        # add year in which game was released
        if ((low.find("year") != -1 or low.find("date") != -1 or
             col == "Release" or col == "Released" or col == "First released") and
            (cn == "")):
            games[name][0] += yr + " | "

        # add game genre
        if (low.find("genre") != -1):
            games[name][1] = t

        # add game developers / programmers
        if (isDev(low)):
            games[name][2] = find_devs(dat)

        # add publishing company, or multiple companies separated by bar
        if (isPub(low)):
            games[name][3] = find_devs(dat)

        # add regions in which game was released
        if (low.find("region") != -1):
            games[name][5] = t

        # add rating information, can be from multiple standards
        if (low.find("esrb") != -1 or low.find("pegi") != -1 or \
            low.find("cero") != -1 or low.find("acb")  != -1):
            games[name][6] += col + " " + t + ", "

        # find misc info / details about a game
        if (low.find("details") != -1 or low.find("description") != -1):
            g = [genre for genre in genres if genre in t.lower()]
            if (not(len(g) < 1)):
                games[name][1] += g[0]

        # check if 'yes' or checked or release date given
        if (yr != "" or t.lower() == "yes" or "check mark" in t.lower()):
            if (cn != ""):
                games[name][5] += cn + ", "
                if (yr != ""):
                    games[name][0] += yr + " " + cn + " | "
    return (games, name)

def parse_name(games, name, title = ""):
    """parses game title for extra info: year, regions. add blank entry to games dict"""
    year = ""
    dev = ""
    regions = ""
    group = m = ""

    # look for all extra information in parantheses
    while (group != None and m != None):
        m = re.search(r'(.*)\(([^\(\)]+)\)(.*)', name)
        if (m):
            name = m.group(1).strip()
            group = m.group(2).strip()
            if (group):
                # add region info
                if (re.match(r'([A-Z]{2}\s*)+', group) or \
                    country(group) != ""):
                    regions += ", ".join([country(g) for g in group.split()]) + " "

                # add release date info
                elif (re.match(r'\*([0-9]{4})\*', group)):
                    year = year(group)

                # otherwise, leave content in parenthesis, and end loop
                else:
                    name += " (" + group + ")"
                    group = None
                    
            name += " " + m.group(3).strip() if m.group(3) != None else ""

    # create a new blank entry for the game
    if True: ###(not name in games) or (games[name][4] == title):
        games[name] = ["",] * 7
        games[name][0] = year
        games[name][2] = dev
        games[name][3] = dev
        games[name][4] = title
        games[name][5] = regions.strip()
        return (games, name)
    else:
        # return blank name if duplicate
        return (games, "")

def post_process(games, name, title):
    """add title to platforms data, remove trailing comma"""
    # add platform info
    games[name][4] += title

    # remove trailing bar from release date info
    games[name][0] = games[name][0].strip(" | ").strip()

    # remove trailing comma from region info
    games[name][5] = games[name][5].strip(", ").strip()

    # remove trailing comma from rating info
    games[name][6] = games[name][6].strip(", ").strip()
    
    return (games, name)

def write_db(games, name, f = None, quiet = True):
    """write games data of [name] to file, tab separated, if opened"""
    # if file is given, not None, then write to file
    if (f):
        if (name != ""):
            # file contents are tab separated, and marked with null if unknown
            data = [name,] + [d if d != "" else "null" for d in games[name]]
            f.write("\t".join(data) + "\n")
        else:
            print("empty name")

    # else, print out data for debugging
    else:
        data = [name,] + [d if d != "" else "null" for d in games[name]]
        quiet or print("\t".join(data))
    
def get_platforms(url):
    """get a list of elements w/ platform data from wiki url"""
    d = pq(url)
    c = d("div#mw-pages")("div.mw-content-ltr")
    return [l.find("a") for l in c("li")]

def mine_wiki_img(img):
    """mine wiki image page, return link to full image"""
    try:
        img = "File:" + img if "File" not in img else img
        url = wiki_base + "/wiki/" + urllib2.quote(img)
        d = pq(url)
    except BaseException:
        print("img error: " + img)
        return ""
    a = d("div.fullImageLink")("a")
    if not a or not 'href' in a[0].keys():
        return ""
    else:
        return "https:" + a[0].attrib['href']

def mine_wiki_info(name, sub_url, info = "vg", depth = 3):
    """mine wiki game page, get cover image, info from infobox"""
    # games = { name : (year, genre, dev, pub, platforms, regions, rating,
    #                   url, img, series, engine, modes, media
    #                   direct, prod, design, prog, artist, writer, composer,
    #                   cabinet, arcade, cpu, sound, display, distributor) }
    attrs = ["release", "genre", "develop", "publish", "platform", "region",
             "rating", "wiki_url", "image", "series", "engine", "mode", "media",
             "direct", "produc", "design", "prog", "artist", "writer", "compose",
             "cabinet", "arcade", "cpu", "sound", "display", "distributor"] \
             if info == "vg" else \
             ["_name", "type", "wiki_url", "logo", "location", "foundation",
              "parent", "predecessor", "successor", "defunct", "fate", 
              "founder", "employees", "people", "equity", "website"]
    print(" mining: " + name)
    try:
        url = api_base + urllib2.quote(sub_url) if api_base not in sub_url else sub_url
        #print(url)
        res = urllib2.urlopen(url, timeout = 30)
        html = str(res.read())
    except BaseException:
        print("error: " + name)
        return ([], {})
    short_url = sub_url #url[url.find("titles=") + len("titles=") :]
    infobox = False
    infoend = False
    names = []
    text = ""

    # retry if pages contains a redirect link
    if len(html) < 2500 and "Infobox" not in html and "infobox" not in html and \
       "#REDIRECT" in html:
        (link, _) = find_wiki_url(html[html.find("#REDIRECT") + 8 :])
        return mine_wiki_info(name, link, info, depth - 1) if depth > 0 else {}

    # return empty dict for missing pages
    if len(html) < 250 and "Infobox" not in html and "infobox" not in html and \
       '"missing"' in html:
        return ([], {})

    # only keep main text of document
    html = html[html.find("wikitext") :]

    games = {}
    games[name] = ["",] * len(attrs)

    uind = [i for (i, a) in zip(range(len(attrs)), attrs) if "wiki_url" in a][0]
    games[name][uind] = short_url

    lines = html.split("\\\\n")
    for line, next in zip(lines, lines[1:]):
        # convert escape chars and unicode chars
        line = preproc(convert(line))
        next = preproc_space(next)

        # irregular end
        if (line.startswith("|}}")) and not (next.startswith("|") or next.startswith("!")):
            infobox = False
            infoend = True
        
        # detect start of infobox
        if "infobox" in line.lower() and not infobox and \
           ((info == "vg" and ("vg" in line.lower() or "game" in line.lower())) or \
            (info != "vg" and ("company" in line.lower()))):
            #print(line)
            infobox = True

        # detect infobox contents
        elif (line.startswith("|") or line.startswith("!") or text) and infobox:
            # add current line to text accumulator
            text += line

            # if next line is a continuation of first, then keep appending
            if (not(next.startswith("|") or next.startswith("!") or \
                    next.startswith("}")) or balanceof(text) > 0) and \
                not(line.endswith("}}") and balanceof(text) < 0):
                continue

            # clean up special characters
            text = text.lstrip("|").lstrip("!")
            text = text.rstrip("}") if balanceof(text) < 0 else text + " "

            # check for no equals sign
            if "=" not in text:
                text = re.sub(r'\s{6,}', "=", text)
                print("no = : " + text + " in " + name)

            # extract field name, value
            field = text[: text.find("=")].lower()
            value = text[text.find("=") + 1 :]

            # clear text, but save temporarily
            prev = text
            text = ""

            ###
            if field.strip().lower() == "image":
                print("uses image: " + name)
            
            # check if title attribute
            if "title" in field and not "file:" in value.lower() and \
               not "image:" in value.lower() and not "italic" in field.lower():
                new_name = unwiki(value)

                # try to maximize name length, so less duplicates are created
                if new_name != name and new_name != "" and \
                   (len(new_name) > len(name) or games[name].count("") < len(attrs) - 1):
                    # if conflicting name, then remove other name
                    if games[name].count("") >= len(attrs) - 1:
                        games.pop(name)
                        
                    name = new_name
                    games[name] = ["",] * len(attrs)
                    games[name][uind] = short_url

            # ignore infobox-specific attributes, distribution, etc
            if not (any([f in field for f in ["italic", "collapsible", "state", "show", "caption", "website", "spinoff", "origin", "_size", "_alt", "padding"]])):
                # find corresponding attribute
                for attr, i in zip(attrs, range(len(attrs))):
                    if attr in field or ("website" in attr and "homepage" in field):
                        #print("found: " + attr)
                        #if "release" in attr:
                        #   print(value)
                        value = mine_wiki_img(get_file(value)) if "image" in attr or "logo" in attr else value
                        value = release(value) if "release" in attr or "foundation" in attr else value
                        value = unwiki(value)
                        value = find_devs(value) if "dev" in attr or "pub" in attr else value
                        value = find_consoles(value) if "platform" in attr else value
                        value = separate(value) if not(any([a in attr for a in ["url", "webs", "page", "image", "logo", "release", "foundation", "defunct", "dev", "pub", "location"]])) else value
                        games[name][i] += " " + value
                        games[name][i] = games[name][i].strip(" \t\n\r")
                        break

            # irregular end
            if line.endswith("}}") and not (next.startswith("|") or next.startswith("!")) and \
               balanceof(line) < 0:
                infobox = False
                infoend = True
        
        # detect end of infobox
        elif (line.startswith("}}") and not (next.startswith("|") or next.startswith("!")) and infobox):
            infobox = False
            infoend = True

        # if end of infobox reached, then request for game to be written to file
        if (infoend and name != "" and name in games):
            names.append(name)
            infoend = False

    return (names, games)
    
def mine_wiki_page(title, url, f = None, games = {}, skip_to_game = None, infobox = False, info = "vg"):
    """mine wiki page for list of video games, return dict of game info"""
    # games = { name : (year, genre, dev, pub, platforms, regions, rating) }
    print("mining: " + title)
    
    response = urllib2.urlopen(url, timeout = 30)
    html = str(response.read())
    header = ""
    endcol = False
    gmlist = False
    islist = False
    table = False
    unbal = False
    rowsp = 0
    data = cols = []
    end_of_page = False
    list_of_games = re.compile(r'[L|l]ist of.*[G|g]ames')

    # read all lines in html document
    for line in html.split("\\\\n"):
        # convert escape chars and unicode chars
        line = convert(line)
        
        # if end of table row, then add data to dict
        if table and data != [] and (line.startswith("|-") or line.startswith("|}")):
            name = ""

            if not infobox:
                # account for rowspan by adding blank columns for each row
                if (rowsp != 0):
                    data = [""] * (len(cols) - len(data)) + data
                    rowsp -= 1
                    
                # ignore row entry if not enough data, doesn't match column
                if (not len(data) < len(cols)):
                    # update games dict
                    for dat, col in zip(data, cols):
                        #print(col + ": " + unwiki(dat))
                        (games, name) = update_games(games, name, unwiki(dat), col)

                # if preceding header contains year info, then update w/ year info
                if year(header) != "":
                    if name != "" and year(header) not in games[name][0]:
                        (games, name) = update_games(games, name, header, "Year")

                # do post processing, then write to database file
                if (name != ""):
                    (games, name) = post_process(games, name, title)
                    write_db(games, name, f)
            else:
                for dat, col in zip(data, cols):
                    # if title element, then follow link
                    low = col.lower()
                    if (info == "vg"  and isTitle(low, dat)) or \
                       (info == "dev" and isDev(low)) or \
                       (info == "pub" and isPub(low)):
                        work_queue.put(dat)
                        #game = (open_wiki_url(dat, f = f, games = games, skip_to_game = skip_to_game))
                        #games.update(game)
                        #skip_to_game = None if game != {} else skip_to_game
                        
            data = []
            unbal = False

        # blank line
        if (len(line) < 1):
            continue

        # detect start of wikitable
        elif "class" in line and "wikitable" in line:
            print("table found")
            table = True
            endcol = False
            cols = []

        # detect wikitable column declarations
        elif line.startswith("!") and table and not endcol:
            cols += map(unwiki, line.strip("!|").split("!!"))

        # end of table column
        elif line.startswith("|}") or \
             (line.startswith("|-") and "sortbottom" in line):
            print("table end")
            table = False
            unbal = False
        elif line.startswith("|-") and table:
            if cols != [] and not endcol:
                endcol = True
                print("cols: " + str(cols))
            continue

        # skip table caption
        elif line.startswith("|+") and table:
            continue

        # skip table header
        elif line.startswith("||") and table:
            continue

        # row entry, can start with "|" or "!" if not in column declaration
        elif (line.startswith("|") or line.startswith("!")) and \
             table and endcol and not unbal:
            if ("rowspan" in line):
                m = re.match(r'.*rowspan\s*=["\s\\]*(\d+).*', line)
                rowsp = int(m.group(1)) if m else 0
                #print("rowsp: " + str(rowsp))
            if ("colspan" in line):
                m = re.match(r'.*colspan\s*=\s*\"?(\d+)\"?\s*.*', line)
                colsp = int(m.group(1)) if m else 0
                line = line.strip("|").strip()
                line = line + ("||" + line) * (colsp - 1)

            # add all lines to data list
            data += bar_split(line.strip("|").strip("!"))

            # determine if brackets in line are unbalanced
            unbal = balanceof(line) != 0
        elif line.startswith("*") and table:
            data[len(data) - 1] += " ".join(bar_split(line.strip("*"))) + " "
        
        # parse headings
        elif line.startswith("=") and line.endswith("="):
            header = line.strip("=")
            hlower = header.lower()
            print("header: " + header)
            # determine if the end of the wiki page is reached
            if ("see also" in hlower or "references" in hlower or
                "external links" in hlower or "footnote" in hlower or
                "update notes" in hlower or "upcoming" in hlower):
                print("unstructured list end")
                gmlist = False
                end_of_page = True

        # parse list
        elif "{{Div col}}" in line and not end_of_page:
            print("list start")
            islist = True

        # parse list item
        elif line.startswith("*") and islist and not table:
            if not infobox:
                (games, name) = parse_name(games, unwiki(line[1:]), title)
                write_db(games, name, f)
            elif info == "vg":
                work_queue.put(line.strip("*"))
                #game = (open_wiki_url(line.strip("*"), f = f, games = games, skip_to_game = skip_to_game))
                #games.update(game)
                #skip_to_game = None if game != {} else skip_to_game
            #print(name)

        # parse end of list
        elif ("{{Div col end}}") in line:
            print ("list end")
            islist = False

        # parse unstructured list
        elif ("list" in line or "List" in line) and \
             re.search(list_of_games, unwiki(line)) and not end_of_page:
            print("unstructured list start")
            gmlist = True

        # parse unstructured list entry
        elif line.startswith("*") and gmlist and not table and \
             not "Exclus" in header and not end_of_page:
            if len(line.split(" ")) < 10 and not "only release" in line:
                if not infobox:
                    (games, name) = parse_name(games, unwiki(line[1:]), title)
                    write_db(games, name, f)
                elif info == "vg":
                    work_queue.put(line.strip("*"))
                    #game = (open_wiki_url(line.strip("*"), f = f, games = games, skip_to_game = skip_to_game))
                    #games.update(game)
                    #skip_to_game = None if game != {} else skip_to_game
                #print(name)

        # otherwise, assume line is part of previous col and append data
        elif table and data != []:
            data[len(data) - 1] += line
            unbal = balanceof(data[len(data) - 1])

    return games

def mine_wiki(f = None, games = {}, skip_to = (None, None), end_at = None, infobox = False, info = "vg"):
    """mine wikipedia list of all video games for info"""
    # games dict: { name : (year, genre, dev, pub, platforms, regions, rating) }
    pfs = get_platforms(wiki) + get_platforms(wiki2)
    (skip_to_plat, skip_to_game) = skip_to

    def readURL(thread_id):
        while (True):
            try:
                # try to retrieve a string from the queue
                dat = work_queue.get(block = False)

                # skip if no url found
                if "[[" not in dat and "]]" not in dat:
                    continue

                # find link in wiki markup text
                (link, name) = find_wiki_url(dat)
                #print("thread " + str(thread_id) + " mining: " + name)

                # if games dict already has the game, then skip
                if name in games:
                    continue

                # mine a single wikipedia game page, in parallel
                (names, new_games) = mine_wiki_info(name, link, info)

                # lock shared resources while writing new data
                lock.acquire()
                
                # write all new games to the database
                for name in names:
                    # only update / write if not already added
                    if not name in games:
                        print("updating: " + name) #print("mining: " + name)
                        games[name] = new_games[name]
                        write_db(games, name, f)

                # unlock after writing to shared resources
                lock.release()
                
            except queue.Empty:
                break

    # set up multithreading
    global work_queue, lock
    N_THREADS = 64
    threads = []
    work_queue = queue.Queue()
    lock = Lock()
    
    titles = []
    for pf in pfs:
        title = pf.text

        # ignore combined pages, redundant pages
        if (title == "List of Commodore 64 games" or
            title == "List of Amiga games" or
            title == "List of PC video games" or
            title == "List of free PC titles"):
            continue
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
            title.find("Xbox One applications") != -1 or
            title.find("3D PlayStation") != -1 or
            title.find("Draft") != -1 or
            title.find("Kinect") != -1):
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
            # ignore kinect fun labs, platinum hits
            continue

        # remove parenthesis / colon for subcategories
        if (title.find(":") != -1):
            title = title[: title.find(":")].strip()
        if (title.find(")") != -1):
            title = title[: title.find("(") - 1].strip()

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
        elif (title.endswith("applications")):
            title = title.replace("applications", "").rstrip()
        elif (title.startswith("games for the original")): # Game Boy
            title = title.replace("games for the original", "").lstrip()
        elif (title.startswith("Xbox games on")): # xbox 360 kinect games
            title = title.replace("Xbox games on", "").lstrip()
        #elif (title.find("Virtual Console games for") != -1):
        #    title = "Virtual Console"
        else:
            # ignore eye toy, exclusives, conversions, accessories, etc
            continue

        # find synonyms for game titles
        if title in synonyms:
            title = synonyms[title]

        if not title in titles:
            titles.append(title)

        # if skip_to parameter given, then stop skipping when reached the desired title
        if skip_to_plat is not None and skip_to_plat == title:
            skip_to_plat = None

        # if end_to parameter given, then stop mining when given title is reached
        if end_at is not None and end_at == title:
            return games

        if not skip_to_plat:
            # for arcade games, visit all subpages instead of parsing main page
            if (title == "arcade"):
                for sub in ["0..9",] + [chr(i) for i in range(ord('A'), ord('Z') + 1)] + ["Not_released",]:
                    games.update(mine_wiki_page(title, api_base + pf.attrib['href'][6:] + ":_" + sub, f, games, skip_to_game, infobox, info))

            # otherwise, use wiki api to find game info, by reading wiki markup source
            else:
                games.update(mine_wiki_page(title, api_base + pf.attrib['href'][6:], f, games, skip_to_game, infobox, info))
            if (not infobox):
                f is None or f.write("\n\n\n")
            skip_to_game = None
            print(title)

    # start all threads
    for i in range(N_THREADS):
        t = Thread(target = readURL, args = (i,))
        t.start()
        threads.append(t)

    # merge all threads when done
    for thread in threads:
        thread.join()

    print(titles)
    return games

def load(f = "games.txt", v = True):
    """load games dict from file, return games info as dict"""
    f = open(f, 'r', encoding = 'utf-8')
    games = {}
    for line in f.readlines():
        line = line.strip().strip("\r\n")
        # ignore blank lines
        if len(line) < 1:
            continue

        # ignore comments
        elif line.startswith("#"):
            continue

        info = line.split("\t")
        name = info[0]
        if name not in games:
            games[name] = info[1:]
        else:
            if name != "" and name != " ":
                print("dup: " + name)
    return games

devs = get_devs()

if __name__ == "__main__":
    f = open('games_wiki.txt', 'a', encoding = 'utf-8')  #games.txt
    #games = mine_wiki(f, games = load("games_wiki.txt"), skip_to = (None, None), infobox = True, info = "vg")
    f.close()
    pass

# TODO - missing PS3 games, need to reupload
# dups - pokemon yellow: special pikachu ed
# split up - pokemon black | white, X | Y
# minecraft stored in db as 'pocket version'
# TODO - use wiki url as key (?) (Portal, Spore)
