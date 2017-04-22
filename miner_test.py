## test functionality of miner.py ##

from pyquery import PyQuery as pq
import miner as m

def test_unwiki():
    # test basic text
    assert (m.unwiki("text") == "text")

    # test italics, link removal
    assert (m.unwiki("''[[Galaxians]]''") == "Galaxians")

    # test link target removal
    assert (m.unwiki("''[[Meteoroids (video game)|Meteoroids]]''") == "Meteoroids")

    # test template removal
    assert (m.unwiki("{{Anchor|0–9}}''[[3 Ninjas Kick Back (video game)|3 Ninjas Kick Back]]''") == "3 Ninjas Kick Back")

    # test style removal
    assert (m.unwiki(" width=16%|Developer<br><ref name=GS/><ref name=GC/>") == "Developer")

    # test tag removal
    assert (m.unwiki("<span style=\"display:none\">7</span>''[[The 7th Saga]]''") == "The 7th Saga")

    # test standalone tag removal
    assert (m.unwiki("Buster Bros. </center>") == "Buster Bros.")

    # test tag removal, w/ inner contents preserved
    assert (m.unwiki("{{vgy|1994}}<sup>NA</sup><br />{{vgy|1995}}<sup>EU, JP</sup><br />") == "1994 NA | 1995 EU, JP")

    # test tag removal, when no end tag present
    assert (m.unwiki("<span id=\"L\">''[[Lalaloopsy: Carnival of Friends]]''") == "Lalaloopsy: Carnival of Friends")

    # test link removal, with multiple links
    assert (m.unwiki("[[Ian Andrew]], [[Chris Andrew]]") == "Ian Andrew, Chris Andrew")

    # test link target removal, with multple links
    assert (m.unwiki("[[Ernieware]], [[David Whittaker (video game composer)|David Whittaker]]") == "Ernieware, David Whittaker")

    # test automatically renamed links, w/ parantheses
    assert (m.unwiki("[[kingdom (biology)|]]") == "kingdom")

    # test automatically renamed links, w/ commas
    assert (m.unwiki("[[Seattle, Washington|]]") == "Seattle")

    # test automatically renamed links, w/ hidden namespace
    assert (m.unwiki("[[Wikipedia:Manual of Style (headings)|]]") == "Manual of Style")

    # remove tags before attempting to remove style attributes
    assert (m.unwiki("<span style=\\\"display:none\\\">Addams F A</span>\'\'[[The Addams Family (video game)|The Addams Family]]\'\'") == "The Addams Family")

    # remove vgy template
    assert (m.unwiki("{{vgy|1994|1994}}") == "1994")

    # remove html comments
    assert (m.unwiki("Seiji Fujihara.{{Citation needed|date=July 2010}}<!--藤原誠司-->") == "Seiji Fujihara.")

    # remove nihongo template
    assert (m.unwiki(" {{Nihongo|'''''D.I.S Airport'''''|Ｄ・Ｉ・Ｓエアポート|D.I.S Eapōto}}") == "D.I.S Airport")

    # remove target links before nihongo template
    assert (m.unwiki("{{Nihongo|'''''[[Shoot 'em up#Golden age and refinement|Kagirinaki Tatakai]]'''''|限りなき戦い}}") == "Kagirinaki Tatakai")

    # remove date template
    assert (m.unwiki("{{dts|2002|03|26}}") == "2002|03|26")
    assert (m.unwiki("{{dts|2014-03-04}}") == "2014-03-04")
    assert (m.unwiki("{{dts|2010|08|}}") == "2010|08|")
    assert (m.unwiki("{{date|2011-02-18|mdy}}") == "2011-02-18")

    # remove time template
    assert (m.unwiki("<span style=\"display:None\">2010-03-04</span> {{#time:F j, Y|2010-3-4 }}") == "2010-3-4")
    assert (m.unwiki("{{#time:F j, Y|}}") == "")

    # remove color template
    assert (m.unwiki("{{color|silver|Unreleased}}") == "Unreleased")

    # remove flagicon template
    assert (m.unwiki("{{Flagicon|US}} {{flagicon|JPN}}") == "US JPN")

    # remove yes / no / console templates
    assert (m.unwiki("{{Yes}}") == "Yes" and m.unwiki("{{No}}") == "No" and m.unwiki("{{Partial|Console}}") == "Partial")
    assert (m.unwiki("{{no|No}}") == "no")

    # remove sort template
    assert (m.unwiki("{{sort|Aeon Flux|''[[Aeon Flux (video game)|Aeon Flux]]''}}") == "Aeon Flux")

    # remove ref template
    assert (m.unwiki("''[[AFL Live 2003]]''{{ref|AUS|[AUS]}}") == "AFL Live 2003")

    # remove check mark, cross template
    assert (m.unwiki("{{check mark|15}}") == "check mark")
    assert (m.unwiki("{{cross|15}}") == "cross")

    # remove vgrelease template, with start date, with multiple companies
    assert (m.unwiki("{{Vgrelease|NA|{{Start date|1983}}}}") == "NA 1983")
    assert (m.unwiki("{{vgrelease|JP=Namco|NA=[[Atari, Inc.]]}}") == "JP Namco | NA Atari, Inc.")
    assert (m.unwiki("{{vgrelease|JP= Pack-In-Video}}{{vgrelease|NA= [[THQ]]}}") == "JP Pack-In-Video NA THQ")
    assert (m.unwiki("{{Video game release||May 12, 2014}}") == "May 12, 2014")

    # remove time template
    assert (m.unwiki("{{#time:F j, Y|2006-05-19}}") == "2006-05-19")

    # remove disambiguation needed template
    assert (m.unwiki("Running Man, The{{dn|date=June 2014}}") == "The Running Man")
    assert (m.unwiki("Plague{{disambiguation needed|date=March 2014}}") == "Plague")

    # remove citation needed template
    assert (m.unwiki("Forgotten Memories: Alternate Realities{{citation needed|date=March 2014}}") == "Forgotten Memories: Alternate Realities")

    # remove unbulleted list template
    assert (m.unwiki("{{ubl|Windows|Xbox|OnLive}}") == "Windows|Xbox|OnLive")

    # remove sc template
    assert (m.unwiki("[[Apple IIGS|Apple II{{sc|gs}}]]") == "Apple IIgs")

    # remove url template
    assert (m.unwiki("{{url|http://www.ndcube.co.jp/ |name=ndcube.co.jp}}") == "http://www.ndcube.co.jp/")

    # expand cpu specs template
    assert (m.unwiki("{{Z80|1|3.072}}") == "1x Z80 @ 3.072 MHz")

    # expand raster details template
    assert (m.unwiki("{{raster|rgb=1|vertical=1|size=19}}") == "RGB raster, vertical orientation (19-inch diagonal)")

    # parse vgrelease new template
    assert (m.unwiki("{{vgrelease new|v=0|NA|1989-03-12|EU|August 16, 2008}}") == "NA 1989-03-12 | EU August 16, 2008")
    assert (m.unwiki("{{vgrelease new|v=1|NA|Cancelled|JP|TBD|EU|TBA|AU|TBA}}") == "NA Cancelled | JP TBD | EU TBA | AU TBA")
    assert (m.year(m.unwiki("{{vgrelease new |JP|1991-12-14||{{vgrelease |NA=July 1992}}")) == "12/14/1991 JP | 1992 NA")

    # remove link with single bracket
    assert (m.unwiki("''[http://www.brutaldeluxe.fr/unreleased/i942.html 1942]") == "1942")
    assert (m.unwiki("[http://www.oxeyegames.com/ Oxeye Game Studio]") == "Oxeye Game Studio")

    # test complex phrases
    assert (m.unwiki("""[[Square (company)|Square Product {{nowrap|Development Division 3}}]]<ref name="production teams">{{cite web |
                     author=Winkler, Chris |year=2003 |title=Square Enix Talks Current Status |url=http://www.rpgfan.com/news/2003/1934.html |work=RPGFan |
                     accessdate=August 1, 2007}}</ref><br />[[Square Enix#Production teams|Square Enix Product {{nowrap|Development Division 3}}]]<ref
                     name="production teams" />""") == "Square Product Development Division 3 | Square Enix Product Development Division 3")

    # sort template removal should be non-greedy
    assert (m.unwiki("{{sort|King of Fighters 2002|''[[The King of Fighters 2002]]''}}{{ref|JP|[JP]}}") == "The King of Fighters 2002")

    # template brackets are automatically balanced, so partial templates should be removed
    assert (m.unwiki("Rayman Legends{{cite web|author=La rédac|title=") == "Rayman Legends")

    # test html comment removal, for single line and multiline comments
    assert (m.unwiki("<!-- Insufficient proof. Only front cover scans found. -->") == "")
    assert (m.unwiki("<!-- See: http://www.smspower.org/db/car_licence-gg-jp.shtml" + 
                     "-- 1) Internal to Mitsubishi Corporation.  Not released outside of the company." +
                     "-- 2) Not a game.") == "")

    # test preserving content inside strikeout tag
    assert (m.unwiki("""<s>''[[Donkey Kong (video game)|Donkey Kong: Original Edition]]''</s> '''(Limited release)''' <ref name="limited release" />""") \
            == "Donkey Kong: Original Edition (Limited release)")

    # make sure html comments and tags are removed properly
    assert (m.unwiki("''[[The Secret Saturdays: Beasts of the 5th Sun]]''<ref>[http://www.gamespot.com/psp/action/thesecretsaturdaysbeastsofthe5thsun/" + 
                     "similar.html?mode=versions The Secret Saturdays: Beasts of the 5th Sun for PSP - The Secret Saturdays: Beasts of the 5th Sun PSP Game - " +
                     "The Secret Saturdays: Beasts of the 5th Sun PSP Video Game<!-- Bot generated title -->]</ref>") == "The Secret Saturdays: Beasts of the 5th Sun")

    # make sure content in center, small, sup tags are preserved
    assert (m.unwiki("''[[F1 (video game)|F1]]''<br><center>''Formula One''<small><sup>BR</sup></small></center> ") == "F1 | Formula One BR")

    # make sure other templates are processed before unbulleted list
    assert (m.separate(m.unwiki("{{unbulleted list| {{yen|1.118 trillion}}")) == 'yen | 1.118 trillion')

def test_split():
    assert (m.bar_split("{{vgy||2007}}") == ["{{vgy|2007}}"])
    assert (m.bar_split("{{vgy}} || {{2007}}") == ["{{vgy}}", "{{2007}}"])

def test_year():
    assert (m.year("1/10/1990") == "1/10/1990")
    assert (m.year("July 12, 2012") == "7/12/2012")
    assert (m.year("23 August 2002") == "8/23/2002")
    assert (m.year("2005-11-23") == "11/23/2005")
    assert (m.year("2002 03 26") == "03/26/2002")
    assert (m.year("1993/07/16") == "07/16/1993")
    assert (m.year("2014") == "2014")
    assert (m.year("1995 EU, JP") == "1995 EU, JP")
    assert (m.year("1994\n\n1995\n") == "1994 | 1995")

    # make sure that 'year' only uses bar separators if multiple years found
    assert (m.year("partial | 2014|2|27") == "2014")    

    # test complex year combinations
    assert (m.year(m.unwiki("|1996-11-26<sup>NA</sup><br>1997-05<sup>UK</sup><br>2001-11-30<sup>UK</sup> (Midway Classics Re-Release)")) ==
            "11/26/1996 NA | 1997 UK | 11/30/2001 UK")

    # test false cases
    assert (m.year("Atari 7800[4]") == "")

def test_reorder():
    assert (m.reorder("Demolition Man") == "Demolition Man")
    assert (m.reorder("Daedalus Encounter, The") == "The Daedalus Encounter")
    assert (m.reorder("Final Quest, The (1991)") == "The Final Quest (1991)")

def test_to_canon():
    assert (m.to_canon("Spinnaker Software Corporation") == "spinnaker")
    assert (m.to_canon("(Open Project)") == "openproject")
    assert (m.to_canon("(VP) Virtual Programming") == "virtualprogramming")
    assert (m.to_canon("Sphere, Inc.") == "sphere")
    assert (m.to_canon("Son Işık") == "sonisik")
    assert (m.to_canon("Jiscsoft Co., Ltd.") == "jiscsoft")
    assert (m.to_canon("PopCap Games") == "popcap")
    assert (m.to_canon("Cryo Interactive Entertainment") == "cryo")
    assert (m.to_canon("Adeline Software International") == "adeline")
    assert (m.to_canon("x media") == "xmedia")
    assert (m.to_canon("Z Software") == "zsoftware")
    assert (m.to_canon("Yab") == "yab")

    assert (m.to_canon("10TACLE Studios") == m.to_canon("10tacle Studios"))
    assert (m.to_canon("4J Studios") == m.to_canon("4JStudios"))
    assert (m.to_canon("Synergy Inc.") == m.to_canon("Synergy, Inc."))
    assert (m.to_canon("ASCII Corporation") == m.to_canon("ASCII Entertainment"))
    assert (m.to_canon("System 3") == m.to_canon("System 3 Software"))
    assert (m.to_canon("Activision (Alan Miller)") == m.to_canon("Activision (David Crane)"))
    assert (m.to_canon("Craft & Meisters") == m.to_canon("Crafts & Meister"))

    assert (m.to_canon("Studio Fish") != m.to_canon("Studio Altair"))
    assert (m.to_canon("B Games") != m.to_canon("B!"))
    assert (m.to_canon("4M Games") != m.to_canon("4M Soft"))
    assert (m.to_canon("AC studio") != m.to_canon("AC LTD."))
    assert (m.to_canon("D Z") != m.to_canon("D'z"))

def test_find_devs():
    assert (m.find_devs(m.unwiki("[[Sphere, Inc.]]")) == "Sphere")
    assert (m.find_devs(m.unwiki("[[Capcom]]/<br>[[Sensory Sweep Studios]]")) \
            == "Capcom | Sensory Sweep")

def test_release():
    assert (m.release("1991") == "1991")
    assert (m.release("1991-2001") == "1991-2001")
    assert (m.release("'''Xbox'''<br />{{vgrelease|NA=May 21, 2002|PAL=July 5, 2002}}'''GameCube'''<br />{{vgrelease|NA=November 18, 2002|PAL=July 11, 2003}}")
            == "Xbox (5/21/2002 NA | 7/5/2002 PAL) | GameCube (11/18/2002 NA | 7/11/2003 PAL)")
    assert (m.release("{{collapsible list|title=July 5, 2002|'''''Soulcalibur II'''''<br />'''Arcade'''<br />{{vgrelease|JP=July 10, 2002|NA=2002}}'''GameCube''', " +
                      "'''PlayStation 2''', & '''Xbox'''<br />{{vgrelease|JP=March 27, 2003|NA=August 27, 2003|EU=September 26, 2003}}'''''HD Online'''''<br />" +
                      '{{vgrelease new|NA|November 19, 2013 <small>(PS3)</small><ref name="HDOnlineReleaseDate">{{cite web |last=Romano |first=Sal |date=' +
                      "October 31, 2013 |url=http://gematsu.com/2013/10/soulcalibur-ii-hd-online-release-date-set |title=Soulcalibur II HD Online release date set " +
                      '|publisher=Gematsu |accessdate=October 31, 2013}}</ref>|EU|November 20, 2013 <small>(PS3)</small><ref name="HDOnlineReleaseDate"/>|JP|' +
                      'February 20, 2014<ref name="JP Date">{{cite web |date=January 27, 2014 |url=http://www.avoidingthepuddle.com/news/2014/1/27/' +
                      "soul-calibur-ii-hd-online-gets-japanese-release-date |title=Soul Calibur II HD Online Gets Japanese Release Date |publisher=Avoiding The " +
                      'Puddle |accessdate=January 29, 2014 (PS3)}}</ref>{{Video game release|WW|November 20, 2013 <small>(X360)</small>' +
                      '<ref name="HDOnlineReleaseDate"/>}}}}}}')
            == "7/5/2002 | Arcade (7/10/2002 JP | 2002 NA) | GameCube, PlayStation 2, & Xbox (3/27/2003 JP | 8/27/2003 NA | 9/26/2003 EU) | " +
               "HD Online (11/19/2013 NA [PS3] | 11/20/2013 EU [PS3] | 2/20/2014 JP | 11/20/2013 WW [X360])")
    assert (m.release("{{collapsible list|title=November 15, 2001|titlestyle=font-weight:normal;font-size:12px;background:transparent;text-align:left|'''Xbox'''" +
                      "<br />{{vgrelease|NA=November 15, 2001<ref name=\"metacritic\"/>|EU=March 14, 2002<ref name=\"auslaunch\">{{cite web|url=" +
                      "http://www.microsoft.com/presspass/press/2002/mar02/03-14globalpr.mspx|title=Xbox Goes Global With European and Australian Launches|date=" +
                      "March 14, 2002|publisher=[[Microsoft]]|accessdate=October 7, 2007}}</ref>}}{{vgrelease|JP=April 25, 2002}}'''Microsoft Windows'''<br />" +
                      "{{vgrelease|NA=September 30, 2003<ref name=\"metacritic2\" />|EU=October 10, 2003<ref name=\"halopc\">{{cite web|url=" +
                      "http://www.gamefaqs.com/pc/291594-halo-combat-evolved/data|title=''Halo: Combat Evolved'' Release Information for PC|publisher=" +
                      "[[GameFAQs]]|accessdate=September 17, 2010}}</ref>}}'''Mac OS X'''<br />December 3, 2003<ref name=\"gamespot\" /><br />" +
                      "'''Games on Demand'''<br />{{vgrelease|NA=December 4, 2007<ref name=\"halo360\">{{cite web|url=http://xbox360.ign.com/" +
                      "objects/142/14218698.html|title=''Halo: Combat Evolved'' - Xbox 360|publisher=IGN|accessdate=September 17, 2010}}</ref>}}}}")
            == "11/15/2001 | Xbox (11/15/2001 NA | 3/14/2002 EU | 4/25/2002 JP) | PC (9/30/2003 NA | 10/10/2003 EU) | " +
               "Mac OS X (12/3/2003) | Games on Demand (12/4/2007 NA)")
    assert (m.release("'''Nintendo DS & GBA''' <sup>[http://www.gamefaqs.com/portable/ds/data/939403.html]</sup><sup>[http://www.gamefaqs.com/portable/gbadvance/" +
                      "data/939404.html]</sup>\n<br />{{vgrelease|NA=October 23, 2007|AUS=February 2008|JP=June 2008}}'''PlayStation 2''' <sup>" +
                      "[http://www.gamefaqs.com/console/ps2/data/939401.html]</sup>\n<br />{{vgrelease|NA=October 23, 2007|EU=February 8, 2008|AUS=February 2008}}" +
                      "'''Wii''' <sup>[http://www.gamefaqs.com/console/wii/data/939402.html]</sup><br />\n{{vgrelease|NA=November 12, 2007|AUS=February 14, 2008}}")
            == "Nintendo DS & GBA (10/23/2007 NA | 2008 AUS | 2008 JP) | PS2 (10/23/2007 NA | 2/8/2008 EU | 2008 AUS) | Wii (11/12/2007 NA | 2/14/2008 AUS)")

def test_mine_wiki_info():
    assert (m.mine_wiki_info("Halo", "Halo:_Combat_Evolved")[1]
            == {'Halo: Combat Evolved':
                ['11/15/2001 | Xbox (11/15/2001 NA | 3/14/2002 EU | 4/25/2002 JP) | PC (9/30/2003 NA | 10/10/2003 EU) | Mac OS X (12/3/2003) | Games on Demand (12/4/2007 NA)',
                 'First-person shooter', 'Bungie | (Xbox and Games on Demand) | Gearbox Software | (Microsoft Windows) | Westlake Interactive | (OS X)',
                 'Microsoft Game Studios | MacSoft (OS X)', 'Xbox | PC | OS X | Xbox 360 (Games On Demand) | Xbox One', '', '', 'Halo:_Combat_Evolved',
                 'https://upload.wikimedia.org/wikipedia/en/8/80/Halo_-_Combat_Evolved_%28XBox_version_-_box_art%29.jpg', 'Halo', '',
                 'Single-player | multiplayer | cooperative', 'Optical disc | Games On Demand (for Xbox360)', '', 'Hamilton Chu', 'John Howard', '',
                 'Marcus Lehto', '', "Martin O'Donnell | Michael Salvatori", '', '', '', '', '', '']})
    assert (m.mine_wiki_info("HL 2", "Half-Life_2")[1]
            == {'Half-Life 2':
                ['11/16/2004 | PC (11/16/2004) | Xbox (11/15/2005 NA | 11/18/2005 EU) | Xbox 360 (10/10/2007 NA | 10/19/2007 EU | 10/25/2007 AUS | 5/22/2008 JP) | ' +
                 'PS3 (12/11/2007 NA | 12/14/2007 EU | 12/20/2007 AUS) | OS X (5/26/2010) | Linux (5/9/2013) | NVIDIA Shield (5/12/2014)', 'First-person shooter', 'Valve Software',
                 'Valve Software | Sierra Entertainment', 'PC | Xbox | Xbox 360 | PS3 | OS X | Linux | Shield Portable', '', '', 'Half-Life_2',
                 'https://upload.wikimedia.org/wikipedia/en/2/25/Half-Life_2_cover.jpg', 'Half-Life', 'Source', 'Single-player', 'Optical disc | download',
                 '', '', '', '', '', '', 'Kelly Bailey', '', '', '', '', '',
                 'Valve Corporation | Vivendi Universal Games (former distributor) | Electronic Arts (2005–present)']})
    assert (m.mine_wiki_info("Hobbit", "The_Hobbit_(2003_video_game)")[1]
            == {'The Hobbit':
                ['PS2/Xbox/GameCube (11/11/2003 NA | 11/28/2003 PAL) | PC (11/10/2003 NA | 11/28/2003 PAL) | Game Boy Advance (11/11/2003 NA | 10/24/2003 PAL)', 'Platform',
                 'Inevitable Entertainment | Saffire (Game Boy Advance)', 'Vivendi Universal | Sierra Entertainment | Saffire (Game Boy Advance)',
                 'Game Boy Advance | PC | GameCube | PS2 | Xbox', '', '', 'The_Hobbit_(2003_video_game)',
                 'https://upload.wikimedia.org/wikipedia/en/c/c3/TheHobbit.jpg', 'Middle-earth', '', 'Single-player',
                 '', '', '', '', '', '', '', '', '', '', '', '', '', '']})
    assert (m.mine_wiki_info("Aeon", "Æon_Flux_(video_game)")[1]
            == {'Aeon': ['PlayStation 2 & Xbox (11/15/2005 NA | 3/31/2006 PAL)', 'Action-adventure', 'Terminal Reality', 'Majesco Entertainment', 'PS2 | Xbox',
                         '', '', 'Æon_Flux_(video_game)', 'https://upload.wikimedia.org/wikipedia/en/9/94/Aeonfluxgame.jpg', '', 'Infernal Engine', 'Single-player',
                         '', '', '', '', '', '', '', '', '', '', '', '', '', '']})
    assert (m.mine_wiki_info("X-Men", "X-Men_Legends")[1]
            == {'X-Men Legends': 
			['GameCube, PS2, Xbox (9/21/2004 NA | 10/22/2004 PAL | 1/27/2005 JP [Xbox only]) | N-Gage (2005 PAL | 2/7/2005 NA)', 'Action role-playing',
             'Raven Software | Barking Lizards (N-Gage)', 'Activision', 'GameCube | N-Gage | PS2 | Xbox', '', '', 'X-Men_Legends',
             'https://upload.wikimedia.org/wikipedia/en/c/c3/X-Men_Legends_Coverart.png', '', 'Vicarious Visions Alchemy',
             'Single-player | Multiplayer (up to 4 players)', '', '', '', '', '', '', '', 'Rik Schaffer', '', '', '', '', '', '']})
    assert (m.mine_wiki_info("Prince", "Prince_of_Persia:_The_Sands_of_Time")[1]
            == {'Prince of Persia: The Sands of Time': 
			['11/6/2003 | PS2 (11/6/2003 NA | 11/21/2003 PAL | 9/2/2004 JP) | Xbox (11/12/2003 NA | 2/20/2004 PAL) | ' +
             'GameCube (11/18/2003 NA | 2/20/2004 PAL) | Game Boy Advance (10/30/2003 NA | 11/14/2003 PAL) | ' +
             'PC (11/30/2003 NA | 12/5/2003 PAL) | Mobile (1/8/2004 NA) | PS3 (11/16/2010 PAL | 11/16/2010 NA)',
             'Puzzle-platformer | action-adventure | hack and slash', 'Ubisoft Montreal', 'Ubisoft | SCEJ',
             'PS2 | Xbox | GameCube | Game Boy Advance | PC | PS3', '', '', 'Prince_of_Persia:_The_Sands_of_Time',
             'https://upload.wikimedia.org/wikipedia/en/8/86/Sands_of_time_cover.jpg', 'Prince of Persia', 'Jade', 'Single-player',
             'Optical disc | Cartridge', 'Patrice Désilets', 'Yannis Mallat', 'Jordan Mechner', 'Claude Langlais', '', 'Jordan Mechner',
             '', '', '', '', '', '', '']})
    assert (m.mine_wiki_info("Madden", "Madden_NFL_2002")[1]
            == {'Madden NFL 2002': 
			['9/12/2001 | GBC & N64 (9/12/2001 NA) | PlayStation (8/13/2001 NA) | PS2 (8/19/2001 NA | 10/12/2001 PAL | 1/31/2002 JP) | ' +
             'PC (8/20/2001 NA | 9/21/2001 PAL) | Xbox (11/15/2001 NA) | GameCube (11/18/2001 NA) | Game Boy Advance (11/20/2001 NA)',
             'Sports (American football)', 'EA Tiburon | Budcat Creations', 'EA Sports',
             'PlayStation | PS2 | Nintendo 64 | GameCube | Xbox | Game Boy Color | Game Boy Advance | PC', '', 'ESRB=E | OFLCA=G | ELSPA=3+',
             'Madden_NFL_2002', 'https://upload.wikimedia.org/wikipedia/en/a/a0/Madden_NFL_2002_Coverart.png', 'Madden NFL', '',
             'Single-player | multiplayer (online support)', '', '', '', '', '', '', '', '', '', '', '', '', '', '']})
    assert (m.mine_wiki_info("Excitebike", "Excitebike")[1]
            == {'Excitebike': ['11/30/1984 | Famicom/NES (11/30/1984 JP | 10/18/1985 NA | 2/3/1986 CA | 9/1/1986 EU) | Arcade (1984 JP | 1985 NA) | NEC PC-8801 (1985 JP) | ' +
                               'Sharp X1 (1985 JP) | Famicom Disk System (12/9/1988 JP) | Game Boy Advance (2/14/2004 JP | 6/2/2004 NA | 7/9/2004 EU) | ' +
                               'Wii (2/16/2007 EU | 3/13/2007 JP | 3/19/2007 NA) | Wii U (4/26/2013 NA | 4/27/2013 EU) | 3D Classics (6/6/2011 JP/NA/EU)',
                               'Racing game', 'Nintendo R&D1 | Hudson Soft (PC-8801, Sharp X1) | Arika (Nintendo 3DS)', 'Nintendo | Hudson Soft (PC-8801, Sharp X1)',
                               'NES | Family Computer | NEC PC-8801 | Sharp X1 | Arcade | Game Boy Advance | GameCube (Animal Crossing) | ' +
                               'Virtual Console (Wii | Wii U) | Nintendo 3DS', '', '', 'Excitebike',
                               'https://upload.wikimedia.org/wikipedia/en/f/f8/Excitebike_cover.jpg', 'Excite', '', 'Single player | multiplayer',
                               'Cartridge | download', '', '', 'Shigeru Miyamoto', '', '', '', 'Akito Nakatsuka', '', '', '', '', '', '']})
    assert (m.mine_wiki_info("Yoshi", "Yoshi_(video_game)")[1]
            == {'Yoshi': ['12/14/1991 | NES/Famicom (12/14/1991 JP | 6/1/1992 NA | 12/10/1992 EU) | Game Boy (12/14/1991 JP | 1992 NA | 12/17/1992 EU) | ' +
             'Wii (3/6/2007 JP | 5/18/2007 AU | 5/18/2007 EU | 7/9/2007 NA | 8/12/2008 KOR) | Ambassador Program (9/1/2011 WW) | ' +
             'Full Version (8/22/2012 JP | 2/21/2013 NA | 5/2/2013 PAL) | Wii U (6/12/2013 WW)', 'Puzzle game', 'Game Freak', 'Nintendo',
             'NES | Famicom | Game Boy | Virtual Console', '', '', 'Yoshi_(video_game)',
             'https://upload.wikimedia.org/wikipedia/en/7/7d/Yoshi_game_cover.jpg', 'Yoshi | Mario', '', 'Single-player | multiplayer',
             '2-megabit cartridge', 'Satoshi Tajiri', 'Shigeru Miyamoto', '', '', '', '', 'Junichi Masuda', '', '', '', '', '', '']})

    # test irregular ending
    assert (m.mine_wiki_info("Cabal", "Cabal_(video_game)")[1]
            == {'Cabal': ['1988', 'Cabal shooter', 'TAD Corporation', 'Taito Corporation | Fabtek',
             'Arcade | Amiga | Amstrad CPC | C64 | ZX Spectrum | DOS | NES', '', '', 'Cabal_(video_game)',
             'https://upload.wikimedia.org/wikipedia/en/1/1d/Cabal_arcadeflyer.png', '', '', 'Single-player | 2 player Co-op',
             '', '', '', '', '', '', '', '', '', '', '', '', '', '']})

    # test that list spanning multiple lines is properly read
    assert (m.mine_wiki_info("Final Fight", "Final_Fight")[1]
            == {'Final Fight': ['1989 | Arcade (1989 INT) | SNES (12/21/1990 JP | 1991 NA | 12/10/1992 PAL) | Final Fight Guy (3/20/1992 JP | 1994 NA) | ' +
                                'Mega-CD Version (4/2/1993 JP | 4/3/1993 NA | 4/4/1993 PAL) | Game Boy Advance (5/25/2001 JP | 9/26/2001 NA | 9/28/2001 PAL)', '',
                                'Capcom', 'Capcom | U.S. Gold Ltd. (computers, Europe) | Ubisoft (GBA, Europe) | Sega (Mega-CD)',
                                'Arcade | Capcom Power System Changer | Amiga | Amstrad CPC | Atari ST | Commodore 64 | PS2 | Mega-CD | ZX Spectrum | Super NES | ' +
                                'Sharp X68000 | Xbox | XBLA | Game Boy Advance | PSP | PlayStation Network | Virtual Console | iOS', '', '', 'Final_Fight',
                                'https://upload.wikimedia.org/wikipedia/en/3/35/Final_Fight_%28flyer%29.jpg', 'Final Fight', '', 'Single player | 2 player co-op',
                                '', '', 'Yoshiki Okamoto', 'Akira Nishitani (Nin-Nin) | Akira Yasuda (Akiman)', '', 'Akira Yasuda', '',
                                'Yoshihiro Sakaguchi | Uncredited: | Yasuaki Fujita | Yoko Shimomura | Kumi Yamaga', 'Upright', 'CP System', '', '',
                                'Raster | 384 x 224 pixels (Horizontal) | 3072 colors', '']})

    # test that TBA strings are processed correctly
    assert (m.mine_wiki_info("Karateka", "Karateka_(video_game)")[1]
            == {'Karateka': ['Apple II (1984 NA) | Atari 8-bit (1985 NA) | Commodore 64 (1985 NA | 1985 EU) | Famicom (12/5/1985 JP) | Atari 7800 (1988 NA) | ' +
                             'CPC, MSX, ZX (1990 EU) | Xbox 360 (11/7/2012 WW) | Windows, PS3 (2012 WW) | iOS (2012 WW) | Wii U (TBA WW) | ' +
                             'Classic [Android, iOS] (5/16/2013 WW)', 'Action', 'Jordan Mechner | Liquid Entertainment (HD Remake)',
                             'Broderbund (original) | D3Publisher (HD Remake)', 'Apple II | Amstrad CPC | Atari 8-bit | Atari 7800 | Atari ST | Commodore 64 | ' +
                             'DOS | Famicom | ZX Spectrum | MSX | Nintendo Game Boy (Original) | Microsoft Windows (Steam) | PlayStation 3 (PlayStation Network) | ' +
                             'Wii U (Nintendo eShop) | Xbox 360 (Xbox Live Arcade) | iOS (HD Remake) | Android and iOS (Classic)', '', '', 'Karateka_(video_game)',
                             'https://upload.wikimedia.org/wikipedia/en/e/ef/Karateka_Coverart.png', '', 'Custom', 'Single-player',
                             'Floppy disk or other | dependent on platform (Original) | Digital download (HD remake and Classic)', '', '',
                             'Jordan Mechner', '', '', '', '', '', '', '', '', '', '']})

    # test that parenthesized content in year text are kept
    assert (m.mine_wiki_info("Nightshade", "Nightshade_(1985_video_game)")[1]
            == {'Nightshade': ['1985 [Spectrum] | 1985 MSX [MSX] | 1986 [Amstrad] | 1986 [Commodore 64]', 'Action-adventure game | Maze game', 'Tim and Chris Stamper',
                               'Ultimate Play The Game', 'ZX Spectrum | Amstrad CPC | BBC Micro | MSX | Commodore 64', '', '', 'Nightshade_(1985_video_game)',
                               'https://upload.wikimedia.org/wikipedia/en/9/9d/Nightshade_title.gif', '', 'Filmation II', 'Single-player', 'Cassette',
                               '', '', '', '', '', '', '', '', '', '', '', '', '']})

    # test that cpu specs are parsed correctly
    assert (m.mine_wiki_info("Xevious", "Xevious")[1]
            == {'Xevious': ['1/29/1983 JP | 1983 NA', 'Vertical scrolling shooter', 'Namco', 'JP Namco NA Atari', 'Arcade | Other', '', '', 'Xevious',
                            'https://upload.wikimedia.org/wikipedia/en/8/8c/Xevious_Poster.png', '', '', 'Up to 2 players | alternating turns', '', '', '',
                            'Masanobu Endo', '', '', '', 'Yuriko Keino', 'Upright', 'Namco Galaga', '3x Z80 @ 3.072 MHz',
                            '1x Namco WSG @ 3.072 MHz | 1x Namco 54XX @ 1.536 MHz', 'Vertical orientation | Raster | 224 x 288', '']})

    # test that Apple ][ is read as Apple II
    assert (m.mine_wiki_info("Odyssey", "Odyssey:_The_Compleat_Apventure")[1]
            == {'Odyssey: The Compleat Apventure':
                ['1980 NA', 'RPG', 'Synergistic Software', 'Synergistic Software', 'Apple II', '', '', 'Odyssey:_The_Compleat_Apventure',
                 '', '', '', '', '', '', '', '', 'Robert Clardy', '', '', '', '', '', '', '', '', '']})

    # test that irregular ends are processed correctly
    assert (m.mine_wiki_info("Shard of Spring", "Shard_of_Spring")[1]
            == {'Shard of Spring': ['1986', 'Role-playing video game', 'TX Digital Illusions', 'Strategic Simulations Inc.', 'Apple II | Commodore 64 | DOS',
                                    '', '', 'Shard_of_Spring', 'https://upload.wikimedia.org/wikipedia/en/8/83/Shard_of_spring.jpg', '', '', 'Single-player',
                                    '', '', '', 'Craig Roth | David Stark', '', '', '', '', '', '', '', '', '', '']})

    # test that refn template is handled correctly
    assert (m.mine_wiki_info("Zelda", "The Legend of Zelda (video game)")[1]
            == {'The Legend of Zelda': 
			['2/21/1986 | Famicom Disk System (2/21/1986 JP) | NES/Famicom (8/22/1987 NA | 11/15/1987 PAL | 2/19/1994 JP) | ' +
             'Game Boy Advance (2/14/2004 JP | 6/2/2004 NA | 7/9/2004 PAL) | Wii (11/19/2006 NA | 12/8/2006 EU) | Ambassador Program (9/1/2011 INT) | ' +
             'Full Version (12/22/2011 JP | 4/12/2012 PAL | 7/5/2012 NA) | Wii U (8/28/2013 JP | 8/29/2013 INT)', 'Action-Adventure', 'Nintendo R&D4',
             'Nintendo', 'Family Computer Disk System | NES | Famicom | GameCube | Game Boy Advance | Virtual Console (Wii | Nintendo 3DS | Wii U)',
             '', '', 'The Legend of Zelda (video game)',
             'https://upload.wikimedia.org/wikipedia/en/4/41/Legend_of_zelda_cover_%28with_cartridge%29_gold.png', 'The Legend of Zelda', '',
             'Single-player', '', 'Shigeru Miyamoto | Takashi Tezuka', 'Shigeru Miyamoto', '', 'Toshihiko Nakago | Yasunari Nishida | Kazuaki Morita',
             '', 'Takashi Tezuka', 'Koji Kondo', '', '', '', '', '', '']})

    # test that efn, sfn templates are removed
    assert (m.mine_wiki_info("Watch Dogs", "Watch Dogs")[1]['Watch Dogs'][1:]
            ==                ['Action-adventure', 'Ubisoft Montreal', 'Ubisoft', 'PC | PS3 | PS4 | Xbox 360 | Xbox One | Wii U', '', '',
                               'Watch Dogs', 'https://upload.wikimedia.org/wikipedia/en/d/d9/Watch_Dogs_box_art.jpg', '', 'Disrupt | with Havok physics',
                               'Single-player | multiplayer', 'Optical disc | download', 'Jonathan Morin', 'Dominic Guay', 'Danny Belanger', 'Francis Boivin', '',
                               'Kevin Shortt', 'Brian Reitzell | Peter Connelly', '', '', '', '', '', ''])

    # test that images w/o brackets are captured
    assert (m.mine_wiki_info("No Man's Sky", "No Man's Sky")[1]
            == {"No Man's Sky": ['2015 WW', '', 'Hello Games', 'Hello Games', 'PS4 | PC', '', '', "No Man's Sky",
                                 'https://upload.wikimedia.org/wikipedia/en/c/ca/No_Mans_Sky_logo.png', '', '', '', '',
                                 'Sean Murray', '', '', '', '', '', '', '', '', '', '', '', '']})

    # test that images w/ exotic characters in title are captured
    assert (m.mine_wiki_info("Pokémon", "Pokémon_Red_and_Blue")[1]
            == {'Pokémon Red Version | Pokémon Blue Version':
                ['Red (2/27/1996 JP | 9/28/1998 NA | 10/23/1998 AUS | 10/5/1999 EU) | Green (2/27/1996 JP) | ' +
                 'Blue (10/15/1996 JP [CoroCoro Comic] | 9/28/1998 NA | 10/23/1998 AUS | 6/10/1999 EU | 10/10/1999 JP [retail])', 'Role-playing video game',
                 'Game Freak', 'Nintendo', 'Game Boy', '', '', 'Pokémon_Red_and_Blue',
                 'https://upload.wikimedia.org/wikipedia/en/e/e9/Pok%C3%A9mon_box_art_-_Red_Version.jpg', 'Pokémon', '', 'Single-player | multiplayer',
                 '4-megabit cartridge', 'Satoshi Tajiri', 'Shigeru Miyamoto | Takashi Kawaguchi | Tsunekazu Ishihara', '', '', 'Ken Sugimori',
                 'Satoshi Tajiri | Ryosuke Taniguchi | Fumihiro Nonomura | Hiroyuki Jinnai', 'Junichi Masuda', '', '', '', '', '', '']})

    # test that pages w/ multiple games are all processed
    assert (m.mine_wiki_info("Puella_Magi_Madoka_Magica", "Puella_Magi_Madoka_Magica")[1]
            == {'Puella Magi Madoka Magica Portable': ['3/15/2012', 'Adventure game | RPG', 'Ban Presto', 'Namco Bandai Games | Nitroplus', 'PSP', '', 'CERO=B',
                                                       'Puella_Magi_Madoka_Magica',
                                                       '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                'Puella Magi Madoka Magica: The Battle Pentagram': ['12/19/2013', 'Action game', 'Artdink', 'Namco Bandai Games', 'Vita', '', '',
                                                                    'Puella_Magi_Madoka_Magica',
                                                                    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']})

    # test that infobox end is detected, even w/ caption field
    assert (m.mine_wiki_info("Star Trek Online", "Star Trek Online")[1]
            == {'Star Trek Online': ['PC (2/2/2010 NA | 2/5/2010 EU | 2/11/2010 AUS) | Mac (3/11/2014 INT)', 'Sci-Fi MMORPG', 'Cryptic Studios',
                                     'Perfect World Entertainment', 'PC | OS X', '', '', 'Star Trek Online',
                                     'https://upload.wikimedia.org/wikipedia/en/e/e2/Star_Trek_Online_cover.jpg', 'Star Trek', 'Cryptic Engine',
                                     'Persistent world | Multiplayer | Third Person Shooter', 'Digital download | DVD-ROM',
                                     '', '', '', '', '', '', '', '', '', '', '', '', '']})

    # test that 'Additional work by:' string in developer text is cleaned
    assert (m.mine_wiki_info("Halo: Reach", "Halo: Reach")[1]
            == {'Halo: Reach': ['9/14/2010 | 9/15/2010 JP', 'First-person shooter', 'Bungie | 343 Industries (Server Control & Anniversary Map Pack) | ' +
                                'Certain Affinity (Defiant Map Pack)', 'Microsoft Game Studios', 'Xbox 360', '', '', 'Halo: Reach',
                                'https://upload.wikimedia.org/wikipedia/en/5/5c/Halo-_Reach_box_art.png', 'Halo', '', 'Single-player | co-op | multiplayer',
                                'Optical disc | download', '', '', '', '', '', '', "Martin O'Donnell | Michael Salvatori", '', '', '', '', '', '']})
            
    # test complex release date text
    assert (m.mine_wiki_info("Minecraft", "Minecraft")[1]
            == {'Minecraft': ['11/18/2011 | Windows, Mac, and Linux (11/18/2011 WW) | Android (10/7/2011 WW) | iOS (11/17/2011 WW) | Xbox 360 [Xbox Live] (5/9/2012 WW) | ' +
                              'Xbox 360 [Retail Disc] (6/4/2013 NA | 6/28/2013 EU) | Raspberry Pi (2/11/2013 WW) | PS3 (12/17/2013 NA | 12/18/2013 EU) | ' +
                              'PS4 (9/4/2014) | Xbox One [Xbox Live] (9/5/2014) | Xbox One [Retail Disc] (11/18/2014) | Vita (10/14/2014 NA | 10/15/2014 EU)',
                              'Sandbox | survival', 'Mojang AB | 4J Studios (console versions)', 'Mojang AB (PC, Mobile) | ' +
                              'Microsoft Studios (Xbox 360, Xbox One, Windows Phone) | Sony Computer Entertainment (PS3, PS4, PS Vita)',
                              'PC | OS X | Linux | Java platform | Java applet | Android | iOS | Windows Phone | Xbox 360 | Xbox One | Raspberry Pi | PS3 | PS4 | Vita',
                              '', '', 'Minecraft', 'https://upload.wikimedia.org/wikipedia/en/3/32/Minecraft_logo.svg', '', '', 'Single-player | multiplayer',
                              'Download | optical disc', '', '', 'Markus Persson (2009–2011) | Jens Bergensten (2011–present)', '',
                              'Kristoffer Zetterstrand | Markus "Junkboy" Toivonen', '', 'Daniel Rosenfeld', '', '', '', '', '', '']})
            
def test_all():
    test_unwiki()
    test_split()
    test_year()
    test_reorder()
    test_to_canon()
    test_find_devs()
    test_release()
    #test_mine_wiki_info()

if __name__ == "__main__":
    test_all()
    print("Tests passed!")
    pass
