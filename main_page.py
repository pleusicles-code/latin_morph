import streamlit as st
from datetime import date, timedelta

st.set_page_config("BevLat", layout="centered")

page_id = "main_page"
st.session_state.curr_page_id = page_id

st.title("Üdvözöl a BevLat!")

#### temporary announcements ####
temp_announcements = [
    {"date": date(2026, 5, 20),
     "text": "Elnézést, ha érintett a hosszú magánhangzók ellenőrzésével kapcsolatos közelmúltbeli hiba. A problémát kijavítottuk!",
    },
    ]
for announcement in [announce["text"] for announce in temp_announcements if announce["date"] >= date.today() - timedelta(days=3)]:
    st.toast(announcement)
##########

st.markdown("""
            A **BevLat** a latin szóalakok (morfológia) gyakorlására szolgáló oldal. 
            A cél a véletlenszerűen adott alakok helyes létrehozása, illetve felismerése, 
            így egyszerre erősítheted meg meglévő tudásodat, 
            és a hibás válaszaidból azt is felismerheted, mely alakokban bizonytalanabb a tudásod. 
            Gyakorolhatod a főneveket, igéket, mellékneveket és határozószókat, igeneveket (jelenleg participiumokat és gerundivumokat), valamint a névmásokat; gyakorolhatod továbbá szófajok és tövek felismerését szótári alakok alapján.
            """)

st.markdown("""
            A BevLat **adatvezérelt**: a korábbi válaszaid alapján 
            gyakrabban kérdezi azokat az alakokat, amelyekkel nehezebben boldogulsz, 
            az egyes szófajokon belüli részletes alkategóriák elemzése alapján. 
            A Statisztikáid és adataid oldalon azt is megnézheted, mely nagyobb kategóriákat lenne érdemes leginkább átismételned.
            """)

st.markdown("""
            A BevLat emellett nagymértékben **testreszabható**: 
            pontosan megadhatod, hogy egy adott szófajon belül mit szeretnél gyakorolni,
            és beállíthatod személyes preferenciáidat többek között a hosszú magánhangzók jelölésére, 
            valamint arra vonatkozóan, milyen információkat kapsz egy-egy szóról.
            """)

st.markdown("""
            Mindezek a funkciók egy **ingyenes fiókkal** működnek a legjobban, 
            amely munkamenetek között is megőrzi az adataidat (a válaszelőzményeket és a beállításaidat); 
            enélkül minden alaphelyzetbe áll minden egyes látogatáskor (vagy akár egy átmeneti hálózati kapcsolatmegszakítás után). 
            A Felhasználói fiók oldalon bármely Google-fiókkal bejelentkezhetsz.
            """)

st.html("""
        <style>
        summary.highlight:hover {
        text-decoration: underline 2px;
        text-underline-position: under;
        }
        </style>
        """)

st.markdown("""
            <details>
            <summary class="highlight">
            <i>Ha <b>először jársz itt</b>, kattints ide néhány hasznos tudnivalóért!</i>
            </summary>

            Első lépésként válassz egy **szófajt**, amelyet gyakorolni szeretnél. 
            A szófajokat az oldalsáv navigációs menüjében találod 
            (ha éppen nincs nyitva, kattints a képernyő bal felső sarkában látható :material/keyboard_double_arrow_right: ikonra).

            Minden szófajhoz számos testreszabható beállítás tartozik, így a BevLat a tudásszintedhez és preferenciáidhoz igazíthatja a feladatokat.
            Ha például még nem tanultad meg egy adott szófaj összes alakját
            (például az igék közül csak a praesens perfectumot, vagy a főnevek közül csak az első és második declinatiót ismered),
            a gyakorlást leszűkítheted az általad már ismert alakokra. 
            Ugyanígy, ha bizonyos alakokat vagy rendhagyó szavakat különösen szeretnél gyakorolni, célzottan kiválaszthatod őket.
            Azt javaslom, hogy amikor egy új alakrendszert tanulsz, kezdetben kevesebb lehetőséget válassz ki, 
            majd fokozatosan adj hozzá újabb alakokat, ahogy egyre biztosabbá válik a tudásod.
            Ha olyan kérdést kapsz, amelyről egyáltalán nincs elképzelésed 
            (például csak a nominativusi és accusativusi alakokat ismered, de dativust kér a program),
            egyszerűen átugorhatod a kérdést.

            Alapértelmezés szerint minden lehetőség ki van választva az egyes szófajoknál. 
            Távolítsd el azokat, amelyeket nem szeretnél gyakorolni 
            (ha csak néhány lehetőséget szeretnél megtartani, 
            gyorsabb lehet először mindet eltávolítani a mező jobb szélén található :material/cancel: ikonra kattintva, 
            majd egyenként visszaadni a kívánt elemeket). 
            Ha nem vagy biztos benne, pontosan mit jelent egy adott beállítás, 
            a hozzá tartozó :material/help: ikon fölé húzva az egeret további információt kaphatsz.

            Miután kiválasztottad a beállításokat, hozd létre az első kérdést a 
            **Kattints ide az első kérdéshez!** gombra kattintva. 
            Miután egyszer rákattintottál, a gomb felirata a munkamenet hátralévő részében, minden szófajnál egyszerűen „Új kérdés” lesz.

            Miután megválaszoltál néhány kérdést, keresd fel a **Statisztikáid és adataid** oldalt, 
            ahol letölthető formában megtalálod a válaszaidat, 
            *és emellett* javaslatokat is kapsz arra, mely kategóriákat lenne érdemes átismételned egy adott szófajon belül, 
            a helyes és hibás válaszaid alapján.

            A BevLat minden funkciója fiók nélkül is használható. 
            Egy fiók létrehozása (egyszerűen Google-fiókkal történő bejelentkezéssel) azonban javítja a felhasználói élményt. 
            A válaszelőzményeid megmaradnak a különböző munkamenetek között, 
            így az adaptív tanulási algoritmus hatékonyabban működik, 
            a Statisztikáid és adataid oldal pontosabban tudja felmérni a gyenge pontjaidat, 
            és internetkapcsolat megszakadása esetén sem veszíted el a haladásodat. 
            (A BevLat offline nem használható, de ha be vagy jelentkezve, a kapcsolat helyreállásakor a válaszaid is helyreállnak.)
            A fiók lehetővé teszi a személyes beállításaid (például a gyakorolni kívánt declinatiók) mentését is, 
            így ezeket nem kell minden alkalommal újra beállítanod, amikor másik szófajra váltasz.
            </details>

            <p></p>

            Ha automatikusan szeretnél továbblépni a következő kérdésre, állítsd be az automatikus továbblépést a navigációs menüben.
            """, unsafe_allow_html=True)


announcements_all = [
    {"date": date(2026, 6, 21),
    "text": """
    Hibás válasz után mostantól megtekintheted az adott alakrendszer **teljes táblázatát**. 
    (Az esetek kívánt sorrendje az oldalsó navigációs menüben állítható be.)
    """,
    },
    {"date": date(2026, 5, 17),
    "text": """
    Mostantól felhasználói fiók is létrehozható!!! Mentsd el a kérdéselőzményeidet több munkameneten keresztül!
    """,
    },
]

announcements = [announcement for announcement in announcements_all if announcement["date"] >= date.today() - timedelta(days=65)]

if len(announcements) > 0:
    st.markdown("""##### Legutóbbi fontos frissítések és hírek""")
    for announcement in announcements:
        st.info(f"{':green-badge[Új!] ' if announcement['date'] >= date.today() - timedelta(days=31) else ''}:blue-badge[{announcement['date'].strftime("%Y-%b-%d")}] {announcement['text']}")

