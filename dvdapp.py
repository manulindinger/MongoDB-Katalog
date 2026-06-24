import curses
from pymongo import MongoClient


# Setup für pymongo
Datenbank = "kinofilme"
Collection = "filme"
Localhost = "mongodb://localhost:27017"

# ASCIIART für Startbildschirm
ASCIIART = r"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#+%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%#=------=-=%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%+-----------:*%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%=-=-=*%%=------:----::-*%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%#------+::------:-:----::-%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%*--:::---:---:-:.-::----:::%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%--------==::-::. :::--:+..:%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%+--:..-::::::-::...::::....*%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%+-::.::.::.:::-::::::::....%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%+-::::-.:: ::::::::::. .  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%-:+-++.  ..:::::::.   .+%%%%%%%%%*   ..:==+#%%%%%%%%%%%
%%%%%%%%%%%%%%#:.. .    .+=:.    ==%%%%%%%%%%%:.          ..%%%%%%%%%
%%%%%%%%%%%%%%%%#:.:-:::::-::-::.:+%%%%%%%%#:.:.       ...::#%%%%%%%%
%%%%%%%%%%%%%%:-=:=+===+***::-:::::-=-%%%#:.....       ..:::#%%%%%%%%
%%%%%%%%%%%%%%=-:::::::::-+::- .=-===++*#-:...:.      ...:::#%%%%%%%%
%%%%%%%%%%%%%%#:::.:::-=.:::-. *#%##*.==-.....:.    . ...:-:#%%%%%%%%
%%%%%=::::=:--::=:::=..-=--+ .  -+-== =.........     ....:::#%%%%%%%%
%%%%%-. .:::-:::..:-: .:...::. :--:. ..:  ......    .....:::#%%%%%%%%
%%%%%%%#%%%%%#::::......  . .:. .-+===:- .+...:..........:::#%%%%%%%%
%%%%%%%%%%%%%#-..:.....-..-.::......:.%%%%*..+..........---:#%%%%%%%%
%%%%%%%%%%%%%#-.:--..-.:=.-.:-.+    +.%%%%*..%%#::::::-----%%%%%%%%%%
%%%%%%%%%%%%%*-......:....-..:.=..:==.%%%%%%..##=.#%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%#...----====+=..-:.:.  .:.=++-...:%+.%*++%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%#:.......:    ..::...::-:-==:::-.---*#---+%%%%%%%
%%%%%%%%%%%=...:%%%%%#-. .     %%%%%%%%%%%%%###%%%%###*=++=%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%+:-:  :-=%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%=-  .* -%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%*:...* -%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%#+#---**#*%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%*-+**==::-::..--*+=:.%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%* .=..--. ==:  .-.=#+ *%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%+ %%+=%% :%%%%#.  %%#  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%# .%%+*%+  %%%%%-  =%%#**%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%=:%%%***  %%%%%%-%  #%%==#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""


# Verbindung
def connect():
    client = MongoClient(Localhost)
    db = client[Datenbank]
    return db[Collection]


# Alle Filme der Datenbank ausgeben (Nur 10 mal sonst zu viel)
def filmliste(coll, stdscr):
    stdscr.clear()
    
    filme = list(coll.find({}, {"_id": 0}))

    if not filme:

        # Fehlermeldung
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(0, 0, "Keine Filme gefunden")
        stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

    else:

        for i, film in enumerate(filme[:10]):
            stdscr.addstr(i * 3, 0, f"{film['name']}:\n Aus {film['jahr']} von {film['regisseur']} - {film['art']} gespielt von: {film['schauspieler']}\n Rating: {film['rating']} ab {film['min_alter']} Jahren [{film['bemerkungen']}]")


    # Hilfemeldung
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
    hoehe, breite = stdscr.getmaxyx()
    stdscr.addstr(hoehe-3, 0, "[X] Taste drücken um abzubrechen")
    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

    # User Input
    stdscr.getch()

# Filmsuche
def filmsuchen(coll, stdscr):
    # Setup
    curses.echo()
    stdscr.clear()

    # Titel
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
    stdscr.addstr(0, 0, "Suche eingeben: ")
    stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)


    p = stdscr.getstr(0, 22, 50).decode("utf-8")
    curses.noecho()

    # NOSQL
    eingabe = {
        "$or": [
            {"name": {"$regex": p, "$options": "i"}},
            {"regisseur": {"$regex": p, "$options": "i"}},
            {"schauspieler": {"$elemMatch": {"$regex": p, "$options": "i"}}}
        ]
    }


    ergebnis = list(coll.find(eingabe, {"_id": 0}))
    stdscr.clear()

    #
    if not ergebnis:

        # Fehlermeldung
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)
        stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
        stdscr.addstr(0, 0, "Keine passende Filme gefunden")
        stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)

    else:
        y = 0
        for film in ergebnis[:10]:

            # Filmname andere Farbe
            curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr(y, 0, f"Name: {film['name']}")
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

            # Andere Daten
            stdscr.addstr(y + 1, 0, f" Art: {film['art']}")
            stdscr.addstr(y + 2, 0, f" Jahr: [{film['jahr']}]")
            stdscr.addstr(y + 3, 0, f" Regie: {film['regisseur']}")
            stdscr.addstr(y + 4, 0, f" Schauspieler: {film['schauspieler']}")
            stdscr.addstr(y + 5, 0, f" Rating: {film['rating']}")
            stdscr.addstr(y + 6, 0, f" Mind. Alter: {film['min_alter']}")

            y += 8  # 8 weil 1 Zeile Abstand

        # Homemenü
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        hoehe, breite = stdscr.getmaxyx()
        stdscr.addstr(hoehe-3, 0, "[X] Taste drücken um abzubrechen")
        stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

    stdscr.getch()

# Einen Film hinzufügen
def hinzufügen(coll, stdscr):
    # Setup
    curses.echo()
    stdscr.clear()

    # Titel
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(0, 0, "Neuer Film hinzufügen:\n")
    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

    # Setup
    datenfelder = ["name", "art", "jahr", "regisseur", "schauspieler", "rating", "min_alter", "bemerkungen"]
    film = {}

    for i, datenfeld in enumerate(datenfelder):

        stdscr.addstr(i + 2, 2, f"{datenfeld}: ")

        value = stdscr.getstr(i + 2, 2 + len(datenfeld) + 2, 50).decode("utf-8")
        if datenfeld in ["art", "schauspieler"]:

            value = [v.strip() for v in value.split(",") if v.strip()]
        elif datenfeld in ["jahr", "min_alter"]:
            
            value = int(value)
        elif datenfeld == "rating":

            value = float(value)
        film[datenfeld] = value

    coll.insert_one(film)
    curses.noecho()

    # Hilfemeldung
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(len(datenfeld) + 10, 0, "[X] Film wurde hinzugefügt.")
    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

    stdscr.getch()

# Film rauslöschen
def löschen(coll, stdscr):
    
    # Setup
    curses.echo()
    stdscr.clear()

    # Titel
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
    stdscr.addstr(0, 0, "Name des Filmes, welcher gelöscht werden soll: \n")
    stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

    # User Input in blau
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
    name = stdscr.getstr(2, 2, 50).decode("utf-8")
    curses.noecho()
    stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)

    # Datenlöschung
    ergebnis2 = coll.delete_one({"name": {"$regex": f"^{name}$", "$options": "i"}})

    # Hilfemeldung
    stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
    hoehe, breite = stdscr.getmaxyx()
    stdscr.addstr(hoehe-3, 0, f"[{ergebnis2.deleted_count}]x Film gelöscht.")
    stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

    stdscr.getch()

    # 2. UI Bugfix
    stdscr.refresh()

def main(stdscr):
    # 1. UI Bugfix
    stdscr.refresh() 

    # Setup
    coll = connect()
    curses.curs_set(0)
    curses.start_color()

    # Farbe
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    # Aktionen
    menu_options = ["[A] Filme anzeigen", "[N] Film hinzufügen", "[S] Film suchen", "[L] Film löschen", "[E] Exit"]

    while True:
        stdscr.clear()

        # Höhe und Breite
        hoehe, breite = stdscr.getmaxyx()
        curses.start_color()

        # Blau und Gelbe Farben
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK) 
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        # Titel
        Titel = "Modul 165 | DVD-Sammlung | by Manuel"
        stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(1, max(0, (breite - len(Titel)) // 2), Titel)
        stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

        art_lines = ASCIIART.strip("\n").splitlines() 


        start_hoehe = 3
        max_art_hoehe = max(0, hoehe - 8)
        stdscr.attron(curses.color_pair(1))

        for i, line in enumerate(art_lines[:max_art_hoehe]):
            text = line[:breite-4] if len(line) > breite-4 else line
            x = max(0, (breite - len(text)) // 2)
            stdscr.addstr(start_hoehe + i, x, text)
        stdscr.attroff(curses.color_pair(1))

        # Anzeige unten
        menu_options = [
            "[A] Filme anzeigen",
            "[N] Film hinzufügen",
            "[S] Film suchen",
            "[L] Film löschen",
            "[E] Exit"
        ]

        menu_hoehe = hoehe - 2
        abstand = breite // len(menu_options)
        for idx, option in enumerate(menu_options):
            xposition = idx * abstand + (abstand - len(option)) // 2
            stdscr.addstr(menu_hoehe, xposition, option)

        stdscr.refresh()
        key = stdscr.getch()

        # Tastendef.
        if key in [ord('a'), ord('A')]:
            filmliste(coll, stdscr)
        elif key in [ord('n'), ord('N')]:
            hinzufügen(coll, stdscr)
        elif key in [ord('s'), ord('S')]:
            filmsuchen(coll, stdscr)
        elif key in [ord('l'), ord('L')]:
            löschen(coll, stdscr)
        elif key in [ord('e'), ord('E')]:
            break
        
# Korrekter Start
if __name__ == "__main__":
    curses.wrapper(main)
