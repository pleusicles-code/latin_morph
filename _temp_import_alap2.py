from pathlib import Path
import py_compile

p = Path("vocab.py")
text = p.read_text(encoding="utf-8")
if "# BEGIN ALAP2 VERBS" in text:
    raise SystemExit("ALAP2 already imported")

verb_block = """
    # BEGIN ALAP2 VERBS
    alap2_verbs = {'accēdō': {'voice': 'act', 'conj': 3, 'meaning': 'odamegy, járul, közeledik', 'pres': 'accēd', 'perf': 'access', 'ppp': 'access'},
     'aestimō': {'voice': 'act', 'conj': 1, 'meaning': 'felbecsül, értékel, vél, gondol', 'pres': 'aestim'},
     'appellō': {'voice': 'act', 'conj': 1, 'meaning': 'megszólít, szól, megnevez, nevez vminek', 'pres': 'appell'},
     'arbitror': {'voice': 'dep', 'conj': 1, 'meaning': 'kikémlel, vél, gondol', 'pres': 'arbitr', 'ppp': 'arbitrāt'},
     'ārdeō': {'voice': 'act', 'conj': 2, 'meaning': 'ég, lángol', 'pres': 'ārd', 'perf': 'ārs', 'fap': 'ārsūr'},
     'armō': {'voice': 'act', 'conj': 1, 'meaning': 'fölszerel, fölfegyverez', 'pres': 'arm'},
     'cēdō': {'voice': 'act', 'conj': 3, 'meaning': 'megy vhová, enged, hátrál', 'pres': 'cēd', 'perf': 'cess', 'ppp': 'cess'},
     'cēnseō': {'voice': 'act', 'conj': 2, 'meaning': 'számba vesz, felbecsül, gondol, indítványoz', 'pres': 'cēns', 'perf': 'cēnsu', 'ppp': 'cēns'},
     'clāmō': {'voice': 'act', 'conj': 1, 'meaning': 'kiabál, szólít, nevez, előhív', 'pres': 'clām'},
     'compleō': {'voice': 'act', 'conj': 2, 'meaning': 'megtölt, megrak, letölt, befejez', 'pres': 'compl', 'perf': 'complēv', 'ppp': 'complēt'},
     'concurrō': {'voice': 'act', 'conj': 3, 'meaning': 'összefut, összecsap, egybeesik', 'pres': 'concurr', 'perf': 'concurs', 'ppp': 'concurs'},
     'conveniō': {'voice': 'act', 'conj': 4, 'meaning': 'összejön, gyülekezik, egyetért', 'pres': 'conven', 'perf': 'convēn', 'ppp': 'convent'},
     'currō': {'voice': 'act', 'conj': 3, 'meaning': 'fut, szalad', 'pres': 'curr', 'perf': 'cucurr', 'ppp': 'curs'},
     'doceō': {'voice': 'act', 'conj': 2, 'meaning': 'tanít, oktat, értesít, kifejt', 'pres': 'doc', 'perf': 'docu', 'ppp': 'doct'},
     'ēveniō': {'voice': 'act', 'conj': 4, 'meaning': 'kijön, megtörténik, sikerül', 'pres': 'ēven', 'perf': 'ēvēn', 'ppp': 'ēvent'},
     'fallō': {'voice': 'act', 'conj': 3, 'meaning': 'megtéveszt, megcsal, elbuktat', 'pres': 'fall', 'perf': 'fefell', 'ppp': 'fals'},
     'fīō': {'voice': 'act', 'conj': None, 'meaning': 'lesz, keletkezik, lesz vmivé', 'ppp': 'fact'},
     'fugiō': {'voice': 'act', 'conj': '3io', 'meaning': 'elfut, -menekül, megfutamodik, elsiet', 'pres': 'fug', 'perf': 'fūg', 'fap': 'fugitūr'},
     'ignōrō': {'voice': 'act', 'conj': 1, 'meaning': 'nem tud, nem ismer', 'pres': 'ignōr'},
     'imperō': {'voice': 'act', 'conj': 1, 'meaning': 'parancsol, követel, uralkodik', 'pres': 'imper'},
     'īnstituō': {'voice': 'act', 'conj': 3, 'meaning': 'felállít, elrendel, bevezet', 'pres': 'īnstitu', 'perf': 'īnstitu', 'ppp': 'īnstitūt'},
     'interficiō': {'voice': 'act', 'conj': '3io', 'meaning': 'meggyilkol, megöl, tönkretesz', 'pres': 'interfic', 'perf': 'interfēc', 'ppp': 'interfect'},
     'interrogō': {'voice': 'act', 'conj': 1, 'meaning': 'kérdez,megkérdez,bevádol', 'pres': 'interrog'},
     'iubeō': {'voice': 'act', 'conj': 2, 'meaning': 'megparancsol, felszólít, utasít, elrendel', 'pres': 'iub', 'perf': 'iuss', 'ppp': 'iuss'},
     'legō': {'voice': 'act', 'conj': 3, 'meaning': 'kiválaszt, összegyűjt, olvas', 'pres': 'leg', 'perf': 'lēg', 'ppp': 'lēct'},
     'mūniō': {'voice': 'act', 'conj': 4, 'meaning': 'megerősít, megvéd, épít', 'pres': 'mūn', 'perf': 'mūnīv', 'ppp': 'mūnīt'},
     'narrō': {'voice': 'act', 'conj': 1, 'meaning': 'elmesél, beszél, mond, előad, említ', 'pres': 'narr'},
     'nesciō': {'voice': 'act', 'conj': 4, 'meaning': 'nem tud, nem ismer', 'pres': 'nesc', 'perf': 'nescīv', 'ppp': 'nescīt'},
     'nōscō': {'voice': 'act', 'conj': 3, 'meaning': 'megismer, tud, észrevesz, megszemlél', 'pres': 'nōsc', 'perf': 'nōv', 'ppp': 'nōt'},
     'numerō': {'voice': 'act', 'conj': 1, 'meaning': 'számlál, olvas, kifizet, valahová sorol', 'pres': 'numer'},
     'patior': {'voice': 'dep', 'conj': '3io', 'meaning': 'elvisel, eltűr, elszenved, enged', 'pres': 'pat', 'ppp': 'pass'},
     'petō': {'voice': 'act', 'conj': 3, 'meaning': 'megy (ahová acc.), törekszik vmire, kér, követel, rátör, siet', 'pres': 'pet', 'perf': 'petīv', 'ppp': 'petīt'},
     'placeō': {'voice': 'act', 'conj': 2, 'meaning': 'tetszik, ,jónak lát, jónak tűnik, vél, elhatároz', 'pres': 'plac', 'perf': 'placu', 'ppp': 'placit'},
     'relinquō': {'voice': 'act', 'conj': 3, 'meaning': 'hátrahagy, életben hagy, átenged, elhagy', 'pres': 'relinqu', 'perf': 'relīqu', 'ppp': 'relict'},
     'repetō': {'voice': 'act', 'conj': 3, 'meaning': 'megismétel, visszamegy, követel', 'pres': 'repet', 'perf': 'repetīv', 'ppp': 'repetīt'},
     'restituō': {'voice': 'act', 'conj': 3, 'meaning': 'visszahelyez, helyére állít, újra felépít, rendbe hoz', 'pres': 'restitu', 'perf': 'restitu', 'ppp': 'restitūt'},
     'rīdeō': {'voice': 'act', 'conj': 2, 'meaning': 'nevet, mosolyog', 'pres': 'rīd', 'perf': 'rīs', 'ppp': 'rīs'},
     'sapiō': {'voice': 'act', 'conj': '3io', 'meaning': 'ízlel, észlel, bölcs, eszes', 'pres': 'sap', 'perf': 'sapi'},
     'sciō': {'voice': 'act', 'conj': 4, 'meaning': 'tud, ismer, ért vmihez', 'pres': 'sc', 'perf': 'scīv', 'ppp': 'scīt'},
     'scrībō': {'voice': 'act', 'conj': 3, 'meaning': 'ír, megír, előad, rajzol', 'pres': 'scrīb', 'perf': 'scrīps', 'ppp': 'scrīpt'},
     'sedeō': {'voice': 'act', 'conj': 2, 'meaning': 'ül, ülésezik, tartózkodik', 'pres': 'sed', 'perf': 'sēd', 'ppp': 'sess'},
     'sentiō': {'voice': 'act', 'conj': 4, 'meaning': 'érez, észrevesz, észlel, vél, gondol', 'pres': 'sent', 'perf': 'sēns', 'ppp': 'sēns'},
     'serviō': {'voice': 'act', 'conj': 4, 'meaning': 'szolgál, kedvében jár, alkalmazkodik', 'pres': 'serv', 'perf': 'servīv', 'ppp': 'servīt'},
     'spērō': {'voice': 'act', 'conj': 1, 'meaning': 'remél', 'pres': 'spēr'},
     'studeō': {'voice': 'act', 'conj': 2, 'meaning': 'fáradozik, igyekszik, törekszik, tanul', 'pres': 'stud', 'perf': 'studu'},
     'taceō': {'voice': 'act', 'conj': 2, 'meaning': 'hallgat, elhallgat vmit, csendben van', 'pres': 'tac', 'perf': 'tacu', 'ppp': 'tacit'},
     'tangō': {'voice': 'act', 'conj': 3, 'meaning': 'érint, elér, bánt, sért', 'pres': 'tang', 'perf': 'tetig', 'ppp': 'tāct'},
     'tendō': {'voice': 'act', 'conj': 3, 'meaning': 'feszít, törekszik, tart vhová', 'pres': 'tend', 'perf': 'tetend', 'ppp': 'tent'},
     'tollō': {'voice': 'act', 'conj': 3, 'meaning': 'felemel, magasba emel, kiemel, megsemmisít', 'pres': 'toll', 'perf': 'sustul', 'ppp': 'sublāt'},
     'valeō': {'voice': 'act', 'conj': 2, 'meaning': 'erős, egészséges, érvényben van', 'pres': 'val', 'perf': 'valu', 'fap': 'valitūr'},
     'volō [repül]': {'voice': 'act', 'conj': 1, 'meaning': 'repül, siet, rohan', 'lemma_lexical': 'volō [repül]', 'pres': 'vol'}}
    _merge_repo_entries(
        verb_vocab,
        alap2_verbs,
        "alap2",
        preserve_core={'legō', 'fugiō', 'fallō', 'fīō', 'sentiō', 'patior'},
    )
    # END ALAP2 VERBS
"""
noun_block = """
    # BEGIN ALAP2 NOUNS
    alap2_nouns = {'aciēs': {'decl': '5_vowel', 'gender': 'f', 'stem': 'aci', 'meaning': 'hegye, éle vminek, csatasor, -rend'},
     'adventus': {'decl': 4, 'gender': 'm', 'stem': 'advent', 'meaning': 'érkezés, jövetel, bekövetkezés'},
     'aetās': {'decl': 3, 'gender': 'f', 'stem': 'aetāt', 'meaning': 'élet, kor, korosztály, korszak'},
     'ager': {'decl': '2_er', 'gender': 'm', 'stem': 'agr', 'meaning': 'szántóföld, föld'},
     'agricola': {'decl': 1, 'gender': 'm', 'stem': 'agricol', 'meaning': 'földművelő, szántóvető'},
     'amīcus': {'decl': '2_us', 'gender': 'm', 'stem': 'amīc', 'meaning': 'barát'},
     'animal': {'decl': '3_istem_neut', 'gender': 'n', 'stem': 'animāl', 'meaning': 'élőlény, állat'},
     'arx': {'decl': 3, 'gender': 'f', 'stem': 'arc', 'meaning': 'fellegvár, védőfal'},
     'auxilium': {'decl': '2_neut', 'gender': 'n', 'stem': 'auxili', 'meaning': 'segítség, segítő csapatok,haderő'},
     'caelum': {'decl': '2_neut', 'gender': 'n', 'stem': 'cael', 'meaning': 'égbolt, légkör, felvilág, égtáj'},
     'clāmor': {'decl': 3, 'gender': 'm', 'stem': 'clāmōr', 'meaning': 'hangos kiáltás, lárma, moraj'},
     'comes': {'decl': 3, 'gender': 'm/f', 'stem': 'comit', 'meaning': 'kísérő, résztvevő, nevelő'},
     'custōdia': {'decl': 1, 'gender': 'f', 'stem': 'custōdi', 'meaning': 'őrzés, őrizet, felügyelet, őrség, fogság'},
     'dea': {'decl': 1, 'gender': 'f', 'stem': 'de', 'meaning': 'istennő'},
     'exitium': {'decl': '2_neut', 'gender': 'n', 'stem': 'exiti', 'meaning': 'kijárat, szabadulás, romlás, pusztulás'},
     'fāma': {'decl': 1, 'gender': 'f', 'stem': 'fām', 'meaning': 'szóbeszéd, hír, közvélemény, hírnév, pletyka'},
     'fēmina': {'decl': 1, 'gender': 'f', 'stem': 'fēmin', 'meaning': 'nő'},
     'ferrum': {'decl': '2_neut', 'gender': 'n', 'stem': 'ferr', 'meaning': 'vas, vasszerszám, fegyver, kard'},
     'fidēs': {'decl': '5_consonant', 'gender': 'f', 'stem': 'fid', 'meaning': 'hit, bizalom, hitelesség, hűség, őszinteség, hihetőség'},
     'fōrma': {'decl': 1, 'gender': 'f', 'stem': 'fōrm', 'meaning': 'alak, forma, szépség'},
     'fuga': {'decl': 1, 'gender': 'f', 'stem': 'fug', 'meaning': 'futás, menekülés'},
     'furor': {'decl': 3, 'gender': 'm', 'stem': 'furōr', 'meaning': 'tombolás, düh, őrültség, rajongás'},
     'geminī': {'decl': '2_us', 'gender': 'm', 'stem': 'gemin', 'meaning': 'ikrek', 'number': 'plural'},
     'gēns': {'decl': '3_istem', 'gender': 'f', 'stem': 'gent', 'meaning': 'nemzetség, rokonság, nép, néptörzs'},
     'ignis': {'decl': '3_istem', 'gender': 'm', 'stem': 'ign', 'meaning': 'tűz, tűzvész, indulat, hév'},
     'imperātor': {'decl': 3, 'gender': 'm', 'stem': 'imperātōr', 'meaning': 'hadvezér, főparancsnok, császár'},
     'īra': {'decl': 1, 'gender': 'f', 'stem': 'īr', 'meaning': 'harag, elkeseredés, düh'},
     'iter': {'decl': '3_neut', 'gender': 'n', 'stem': 'itiner', 'meaning': 'út, ösvény'},
     'iūdex': {'decl': 3, 'gender': 'm', 'stem': 'iūdic', 'meaning': 'bíró'},
     'iūdicium': {'decl': '2_neut', 'gender': 'n', 'stem': 'iūdici', 'meaning': 'ítélet, döntés, vélemény, vizsgálat'},
     'iūs': {'decl': '3_neut', 'gender': 'n', 'stem': 'iūr', 'meaning': 'jog(szabály), törvény, ,jogrend'},
     'iussus': {'decl': 4, 'gender': 'm', 'stem': 'iuss', 'meaning': 'parancs'},
     'lacrima': {'decl': 1, 'gender': 'f', 'stem': 'lacrim', 'meaning': 'könny'},
     'latus': {'decl': '3_neut', 'gender': 'n', 'stem': 'later', 'meaning': 'oldal', 'lemma_lexical': 'latus [főnév]'},
     'lēx': {'decl': 3, 'gender': 'f', 'stem': 'lēg', 'meaning': 'törvény, rendeltetés, végzet, rend'},
     'littera': {'decl': 1, 'gender': 'f', 'stem': 'litter', 'meaning': 'betű; (pl.) írás, levél irodalom, könyvek'},
     'lūx': {'decl': 3, 'gender': 'f', 'stem': 'lūc', 'meaning': 'világ, napvilág, világosság, élet'},
     'magistrātus': {'decl': 4, 'gender': 'm', 'stem': 'magistrāt', 'meaning': 'tisztség, hivatal, tisztségviselő'},
     'maiōrēs': {'decl': 3, 'gender': 'm', 'stem': 'maiōr', 'meaning': 'az idősebbek, az ősök, az öregek', 'number': 'plural'},
     'malum': {'decl': '2_neut', 'gender': 'n', 'stem': 'mal', 'meaning': 'rossz dolog, hiba, gyarlóság, baj, kár'},
     'manus': {'decl': 4, 'gender': 'f', 'stem': 'man', 'meaning': 'kéz, csapat, családfői hatalom'},
     'moenia': {'decl': '3_istem_neut', 'gender': 'n', 'stem': 'moen', 'meaning': 'városfal, védőbástya', 'number': 'plural'},
     'mōs': {'decl': 3, 'gender': 'm', 'stem': 'mōr', 'meaning': 'szokás, akarat, szabály, törvény'},
     'mulier': {'decl': 3, 'gender': 'f', 'stem': 'mulier', 'meaning': 'asszony, nő'},
     'numerus': {'decl': '2_us', 'gender': 'm', 'stem': 'numer', 'meaning': 'szám'},
     'nūntius': {'decl': '2_us', 'gender': 'm', 'stem': 'nūnti', 'meaning': 'hírvivő, követ, küldött, üzenet, hír'},
     'oculus': {'decl': '2_us', 'gender': 'm', 'stem': 'ocul', 'meaning': 'szem'},
     'odium': {'decl': '2_neut', 'gender': 'n', 'stem': 'odi', 'meaning': 'gyűlölet'},
     'opera': {'decl': 1, 'gender': 'f', 'stem': 'oper', 'meaning': 'munka, mű, tevékenység'},
     'poēta': {'decl': 1, 'gender': 'm/f', 'stem': 'poēt', 'meaning': 'költő'},
     'potestās': {'decl': 3, 'gender': 'f', 'stem': 'potestāt', 'meaning': 'erő, hatalom, uralom, hivatal, képesség'},
     'praeda': {'decl': 1, 'gender': 'f', 'stem': 'praed', 'meaning': 'zsákmány, nyereség, haszon'},
     'proelium': {'decl': '2_neut', 'gender': 'n', 'stem': 'proeli', 'meaning': 'csata, harc'},
     'prōvincia': {'decl': 1, 'gender': 'f', 'stem': 'prōvinci', 'meaning': 'tartomány'},
     'rēgīna': {'decl': 1, 'gender': 'f', 'stem': 'rēgīn', 'meaning': 'királynő, királyné, úrnő'},
     'regiō': {'decl': 3, 'gender': 'f', 'stem': 'regiōn', 'meaning': 'vidék, táj'},
     'religiō': {'decl': 3, 'gender': 'f', 'stem': 'religiōn', 'meaning': 'vallás(osság), szertartás, eskü'},
     'repetītiō': {'decl': 3, 'gender': 'f', 'stem': 'repetītiōn', 'meaning': 'ismétlés'},
     'Rōmulus': {'decl': '2_us', 'gender': 'm', 'stem': 'Rōmul', 'meaning': 'Romulus, Róma alapítója', 'number': 'singular'},
     'saeculum': {'decl': '2_neut', 'gender': 'n', 'stem': 'saecul', 'meaning': 'emberöltő, kor, idő, század'},
     'scelus': {'decl': '3_neut', 'gender': 'n', 'stem': 'sceler', 'meaning': 'bűn, gaztett, gonoszság, álnokság'},
     'scientia': {'decl': 1, 'gender': 'f', 'stem': 'scienti', 'meaning': 'ismeret, tudás, szakértelem, tudomány'},
     'sēdēs': {'decl': '3_istem', 'gender': 'f', 'stem': 'sēd', 'meaning': 'ülőhely, szék, lakás, színhely, székhely'},
     'sententia': {'decl': 1, 'gender': 'f', 'stem': 'sententi', 'meaning': 'mondat, nézet, vélemény, ítélet, gondolat'},
     'servus': {'decl': '2_us', 'gender': 'm', 'stem': 'serv', 'meaning': 'szolga, rabszolga'},
     'socius': {'decl': '2_us', 'gender': 'm', 'stem': 'soci', 'meaning': 'társ, részes, szövetséges'},
     'speciēs': {'decl': '5_vowel', 'gender': 'f', 'stem': 'speci', 'meaning': 'külalak, megjelenés, kép, látszat, fajta'},
     'spēs': {'decl': '5_consonant', 'gender': 'f', 'stem': 'sp', 'meaning': 'remény, várakozás'},
     'studium': {'decl': '2_neut', 'gender': 'n', 'stem': 'studi', 'meaning': 'törekvés, igyekezet, érdeklődés, vmivel való foglalkozás'},
     'taurus': {'decl': '2_us', 'gender': 'm', 'stem': 'taur', 'meaning': 'bika'},
     'tēlum': {'decl': '2_neut', 'gender': 'n', 'stem': 'tēl', 'meaning': 'fegyver, dárda, nyíl, támadófegyver'},
     'Tiberis': {'decl': '3_istem', 'gender': 'm', 'stem': 'Tiber', 'meaning': 'Tiberis folyó', 'number': 'singular', 'true_i_stem': True, 'irreg': {'sg': {'acc': 'Tiberim', 'abl': 'Tiberī'}}},
     'vēritās': {'decl': 3, 'gender': 'f', 'stem': 'vēritāt', 'meaning': 'valóság, igazság, őszinteség'},
     'victor': {'decl': 3, 'gender': 'm', 'stem': 'victōr', 'meaning': 'győztes, győző'},
     'victōria': {'decl': 1, 'gender': 'f', 'stem': 'victōri', 'meaning': 'győzelem, siker'},
     'voluntās': {'decl': 3, 'gender': 'f', 'stem': 'voluntāt', 'meaning': 'akarat'},
     'vōx': {'decl': 3, 'gender': 'f', 'stem': 'vōc', 'meaning': 'hangzás, hang'},
     'vulgus': {'decl': '2_neut', 'gender': 'n', 'stem': 'vulg', 'meaning': 'tömeg, sokaság, köznép, csőcselék'}}
    _merge_repo_entries(
        noun_vocab,
        alap2_nouns,
        "alap2",
        preserve_core={'fēmina', 'spēs', 'aciēs', 'vōx', 'dea', 'agricola', 'manus', 'animal', 'speciēs', 'amīcus', 'servus', 'ager', 'ignis', 'fidēs'},
    )
    # END ALAP2 NOUNS
"""
adj_block = """
    # BEGIN ALAP2 ADJECTIVES
    alap2_adjectives = {'aeternus': {'meaning': 'örök, elmúlhatatlan', 'decl': (1, 2), 'stem': 'aetern'},
     'antīquus': {'meaning': 'régi, ősi', 'decl': (1, 2), 'stem': 'antīqu'},
     'barbarus': {'meaning': 'barbár, külföldi, műveletlen, durva, vad', 'decl': (1, 2), 'stem': 'barbar'},
     'beātus': {'meaning': 'gazdag, vagyonos, boldog', 'decl': (1, 2), 'stem': 'beāt'},
     'doctus': {'meaning': 'iskolázott, tanult, művelt, ,jártas', 'decl': (1, 2), 'stem': 'doct'},
     'duo': {'meaning': 'két, kettő', 'decl': 3, 'stem': 'du'},
     'extrēmus': {'meaning': 'legvégső, legutolsó, legnagyobb, szélső', 'decl': (1, 2), 'stem': 'extrēm'},
     'falsus': {'meaning': 'téves, álnok, csalárd, hazug, megtévesztett', 'decl': (1, 2), 'stem': 'fals'},
     'fortis': {'meaning': 'bátor, vitéz, erős', 'decl': 3, 'stem': 'fort', 'noms': ('fortis', 'forte')},
     'gracilis': {'meaning': 'karcsú, nyulánk, vékony, szűkös, dísztelen', 'decl': 3, 'stem': 'gracil', 'noms': ('gracilis', 'gracile')},
     'illūstris': {'meaning': 'világos, ragyogó, híres, kiváló', 'decl': 3, 'stem': 'illūstr', 'noms': ('illūstris', 'illūstre')},
     'immortālis': {'meaning': 'halhatatlan, örökkévaló, boldog', 'decl': 3, 'stem': 'immortāl', 'noms': ('immortālis', 'immortāle')},
     'inimīcus': {'meaning': 'ellenséges, barátságtalan', 'decl': (1, 2), 'stem': 'inimīc'},
     'lātus': {'meaning': 'széles, tágas, nagyképű, hosszadalmas', 'lemma_lexical': 'lātus [melléknév]', 'decl': (1, 2), 'stem': 'lāt'},
     'medius': {'meaning': 'középső, középen levő', 'decl': (1, 2), 'stem': 'medi'},
     'prīmus': {'meaning': 'első, kezdő, legkiválóbb', 'decl': (1, 2), 'stem': 'prīm'},
     'prīvātus': {'meaning': 'vmitől megfosztott, magán, magános, mindennapi', 'decl': (1, 2), 'stem': 'prīvāt'},
     'pūblicus': {'meaning': 'állami, hivatalos, nyilvános, közös', 'decl': (1, 2), 'stem': 'pūblic'},
     'quālis': {'meaning': 'milyen, miféle,melyik, amilyen, amelyik', 'decl': 3, 'stem': 'quāl', 'noms': ('quālis', 'quāle')},
     'quantus': {'meaning': 'mennyi, mekkora, amennyi, amekkora', 'decl': (1, 2), 'stem': 'quant'},
     'rēctus': {'meaning': 'egyenes, helyes, becsületes', 'decl': (1, 2), 'stem': 'rēct'},
     'reliquus': {'meaning': 'többi, maradék, hátrahagyott+E248 ', 'decl': (1, 2), 'stem': 'reliqu'},
     'secundus': {'meaning': 'következő, második, másodrendű, kedvező', 'decl': (1, 2), 'stem': 'secund'},
     'sōlus': {'meaning': 'egyedüli, egyetlen, magányos', 'decl': (1, 2), 'stem': 'sōl', 'pronominal': True},
     'summus': {'meaning': 'legfelső, teljes', 'decl': (1, 2), 'stem': 'summ'},
     'tacitus': {'meaning': 'hallgatag, szótlan, csendes, titkos', 'decl': (1, 2), 'stem': 'tacit'},
     'tālis': {'meaning': 'ilyen, olyan', 'decl': 3, 'stem': 'tāl', 'noms': ('tālis', 'tāle')},
     'tantus': {'meaning': 'akkora, annyi', 'decl': (1, 2), 'stem': 'tant'},
     'tertius': {'meaning': 'harmadik', 'decl': (1, 2), 'stem': 'terti'},
     'tōtus': {'meaning': 'egész, teljes, minden, összes', 'decl': (1, 2), 'stem': 'tōt', 'pronominal': True},
     'trēs': {'meaning': 'három', 'decl': 3, 'stem': 'tr'},
     'ūnus': {'meaning': 'egy, egyik', 'decl': (1, 2), 'stem': 'ūn', 'pronominal': True},
     'ūtilis': {'meaning': 'használható, alkalmas vmire', 'decl': 3, 'stem': 'ūtil', 'noms': ('ūtilis', 'ūtile')},
     'validus': {'meaning': 'erős, érvényes', 'decl': (1, 2), 'stem': 'valid'},
     'vērus': {'meaning': 'igaz, igazi, valódi', 'decl': (1, 2), 'stem': 'vēr'},
     'senex': {'decl': 3,
               'stem': 'sen',
               'noms': ('senex',),
               'meaning': 'agg, öreg, vén',
               'comp': None,
               'super': None,
               'no_adv': True,
               'irreg': {'forms': {'sg': {'nom': ('senex', 'senex', 'senex'),
                                          'voc': ('senex', 'senex', 'senex'),
                                          'gen': ('senis', 'senis', 'senis'),
                                          'dat': ('senī', 'senī', 'senī'),
                                          'acc': ('senem', 'senem', 'senex'),
                                          'abl': ('sene', 'sene', 'sene')},
                                    'pl': {'nom': ('senēs', 'senēs', 'senēs'),
                                           'voc': ('senēs', 'senēs', 'senēs'),
                                           'gen': ('senum', 'senum', 'senum'),
                                           'dat': ('senibus', 'senibus', 'senibus'),
                                           'acc': ('senēs', 'senēs', 'senēs'),
                                           'abl': ('senibus', 'senibus', 'senibus')}}}}}
    _merge_repo_entries(
        adj_vocab,
        alap2_adjectives,
        "alap2",
        preserve_core={'sōlus', 'fortis', 'trēs', 'duo', 'ūnus'},
    )
    # END ALAP2 ADJECTIVES
"""

text = text.replace("    # END ALAP1 VERBS\n", "    # END ALAP1 VERBS\n" + verb_block, 1)
text = text.replace("    # END ALAP1 NOUNS\n", "    # END ALAP1 NOUNS\n" + noun_block, 1)
text = text.replace("    # END ALAP1 ADJECTIVES\n", "    # END ALAP1 ADJECTIVES\n" + adj_block, 1)

if "# BEGIN ALAP2 VERBS" not in text or "# BEGIN ALAP2 NOUNS" not in text or "# BEGIN ALAP2 ADJECTIVES" not in text:
    raise SystemExit("Could not locate one or more ALAP1 markers")

misc_block = """

# BEGIN ALAP2 MISC
def import_misc():
    misc_vocab = {'aiō': {'meaning': 'igent mond, így szól, állít, azt mondja', 'lexical_only': True, 'source_pos': 'verb', 'dictionary_entry': 'aiō, ait', 'lemma_lexical': 'aiō'},
     'coepī': {'meaning': 'kezdett, megkezdődött, kezd', 'lexical_only': True, 'source_pos': 'verb', 'dictionary_entry': 'coepī, coepisse, coeptum'},
     'ōdī': {'meaning': 'gyűlöl, utál, megvet', 'lexical_only': True, 'source_pos': 'verb', 'dictionary_entry': 'ōdī, ōdisse, ōsus sum'},
     'oportet': {'meaning': 'kell, illik, célszerű', 'lexical_only': True, 'source_pos': 'verb', 'dictionary_entry': 'oportet 2 oportuit'},
     'rēs pūblica': {'meaning': 'közügy, köztársaság, állam, államhatalom, államvagyon', 'lexical_only': True, 'source_pos': 'noun', 'dictionary_entry': 'rēs pūblica, reī pūblicae f.'}}
    for data in misc_vocab.values():
        data["repo"] = "alap2"
    return misc_vocab
# END ALAP2 MISC
"""
text += misc_block
p.write_text(text, encoding="utf-8")

diag = Path("inflection_tables.py")
dtext = diag.read_text(encoding="utf-8")
old = 'else:\n    st.info("Az alap1 repóban jelenleg nincs külön importált névmási állomány.")'
new = 'else:\n    st.info("Ehhez a szóhoz jelenleg nincs morfológiai ragozási tábla a diagnosztikai oldalon.")'
if old in dtext:
    dtext = dtext.replace(old, new, 1)
diag.write_text(dtext, encoding="utf-8")

py_compile.compile("vocab.py", doraise=True)
py_compile.compile("inflection_tables.py", doraise=True)
