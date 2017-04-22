## test functionality of miner_old.py ##

from pyquery import PyQuery as pq
import miner_old as m

def test_text():
    assert (m.text(pq("text")) == "text")
    assert (m.text(pq("<i>italics</i>")) == "italics")
    assert (m.text(pq("<a href=\"wikipedia.org\">link</a>")) == "link")
    assert (m.text(pq("<td><i>D & D: Slayer</i><br><i>D & D: Dungeon</i></td>")) \
            == "D & D: Slayer\n" + "D & D: Dungeon")
    assert (m.text(pq("2002<span class=\"flagicon\"><a href=\"wiki/Japan\" title=\"Japan\"></a></span>2003")) \
            == "2002 JP\n" + "2003")
    assert (m.text(pq("<a href=wiki/vid>Another World</a><sup>EU</sup><br>" +\
                          "<i>Out of This World</i><sup>NA</sup>"), no_sup = True) \
            == "Another World\nOut of This World")

def test_year():
    assert (m.year("1/10/1990") == "1990")
    assert (m.year("July 4, 2012") == "2012")
    assert (m.year("2005-11-23") == "2005")
    assert (m.year("2014") == "2014")
    assert (m.year("1995 EU, JP") == "1995 EU, JP")
    assert (m.year("1994\n\n1995\n") == "1994 | 1995")

def test_reorder():
    assert (m.reorder("Demolition Man") == "Demolition Man")
    assert (m.reorder("Daedalus Encounter, The") == "The Daedalus Encounter")

def test_all():
    test_text()
    test_year()
    test_reorder()

if __name__ == "__main__":
    test_all()
    print("Tests passed!")
