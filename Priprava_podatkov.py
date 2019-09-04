import re
import os
import csv

# ------ kopirano od profesorja ------


def pripravi_imenik(ime_datoteke):
    '''Če še ne obstaja, pripravi prazen imenik za dano datoteko.'''
    imenik = os.path.dirname(ime_datoteke)
    if imenik:
        os.makedirs(imenik, exist_ok=True)


def vsebina_datoteke(ime_datoteke):
    '''Vrne niz z vsebino datoteke z danim imenom.'''
    with open(ime_datoteke, encoding='utf-8') as datoteka:
        return datoteka.read()


def zapisi_csv(slovarji, imena_polj, ime_datoteke):
    '''Iz seznama slovarjev ustvari CSV datoteko z glavo.'''
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as csv_datoteka:
        writer = csv.DictWriter(csv_datoteka, fieldnames=imena_polj)
        writer.writeheader()
        for slovar in slovarji:
            writer.writerow(slovar)

# ------ moja koda ------


kazalo = os.getcwd() + "\\podatki\\kazalo.html"


vzorec_teden = re.compile(
    r'<a href=\"(?P<Teden>\d+-\d+-\d+)\.html\"'
)


def seznam_tednov(kazalo):
    '''Naredi seznam datotek, po katerih bomo brali'''
    vsebina_kazala = vsebina_datoteke(kazalo)
    seznam = []
    for ujemanje in vzorec_teden.finditer(vsebina_kazala):
        seznam.append(ujemanje.group('Teden'))
    return seznam


def datoteka_tedna(teden):
    return os.getcwd() + "\\podatki\\" + teden + ".html"


vzorec_Ward_Updates = re.compile(r'<h2><u>Ward Updates</u></h2>.*?<br><br>', flags=re.DOTALL)

# od 2017-12-30 dalje imajo napako da manjka </a>
vzorec_New_Fics = re.compile(r'<h2><u><a name="new-fic">New Fics(</a>)?</u></h2>.*?<br><br>', flags=re.DOTALL)

vzorec_New_Quests = re.compile(r'<h2><u><a name="new-quest">New Quests(</a>)?</u></h2>.*?<br><br>', flags=re.DOTALL)

vzorec_Completed_Fics = re.compile(r'<h2><u><a name="completed-fic">Completed Fics(</a>)?</u></h2>.*?<br><br>', flags=re.DOTALL)

vzorec_One_shot_Fics = re.compile(r'<h2><u><a name="one-shot-fic">One-shot Fics(</a>)?</u></h2>.*?<br><br>', flags=re.DOTALL)

vzorec_Revived_Fics = re.compile(r'<h2><u><a name="revived-fic">Revived Fics(</a>)?</u></h2>.*?<br><br>', flags=re.DOTALL)

vzorec_Revived_Quests = re.compile(r'<h2><u><a name="revived-quest">Revived Quests(</a>)?</u></h2>.*?<br><br>', flags=re.DOTALL)

vzorec_Updated_Fics = re.compile(r'<h2><u><a name="updated-fic">Updated Fics(</a>)?</u></h2>.*?<br><br>', flags=re.DOTALL)

vzorec_Updated_Quests = re.compile(r'<h2><u><a name="updated-quest">Updated Quests(</a>)?</u></h2>.*?<br><br>', flags=re.DOTALL)

vzorec_bloka = re.compile(r'<hr><article.*?</article>', flags=re.DOTALL)

vzorec_naslov = re.compile(r'<b><a href=".*?"( title=".*?")?>(?P<Naslov>.*?)</a>', flags=re.DOTALL)

vzorec_update = re.compile(
    r'\((?P<Update_chapters>\d+) new chapters?, (?P<Update_words>\d+\.?\d?)(?P<Update_K>k?) words\)'
)

# nekateri avtorji nimajo linkov. 3 ure sm to gruntov T_T
vzorec_author = re.compile(r'<br><b>Author:</b> (<a href=".*?">)?(?P<Author>.*?)(</a>)?(</b>)?\n')
vzorec_author_alt = re.compile(r'by <a href=".*?">(?P<Author>.*?)</a>')
vzorec_author_alt_2 = re.compile(r'by (?P<Author>.*?)</b>')

# dodal možnost m
# dodal NaNt, ker je par ficov pri katerih je to podatek.
# dodal (<a href=".*?">)? za fice pred 2017-8-19
vzorec_total = re.compile(
    r'<br><b>Total length:</b> (<a href=".*?">)?(?P<Total_chapters>\d+) chapters?, '
    r'(?P<Total_words>\d+\.?\d?)?(?P<Total_K>k?)?(?P<Total_M>m?)(?P<NaNt>NaNt)? words',
    flags=re.DOTALL
)

vzorec_vseh_strani = re.compile(r'\(<a href=".*?"(?P<Strani>>.*?</a>)\)')

vzorec_posameznih_strani = re.compile(r'>(?P<Stran>.*?)</a>')

vzorec_date_created = re.compile(
    r'<br><b>Created on:</b> (?P<Date_created>.*?)<'
)

vzorec_date_updated = re.compile(
    r'<br><b>Updated on:</b> (?P<Date_updated>.*?)<'
)

def izloci_strani(strani):
    '''iz stringa v katerem so strani naredi seznam strani'''
    seznam_strani = []
    for stran in vzorec_posameznih_strani.finditer(strani):
        seznam_strani.append(stran.group('Stran'))
    return seznam_strani

def izloci_podatke_fic(blok, teden, quest, complete):
    '''iz stringa blok pobere podatke'''

    naslov = vzorec_naslov.search(blok).group('Naslov')

    author = vzorec_author.search(blok)
    if author:
        author = author.group('Author')
    elif vzorec_author_alt.search(blok):
        author = vzorec_author_alt.search(blok).group('Author')
    else:
        author = vzorec_author_alt_2.search(blok).group('Author')

    # ta gotovo obstaja
    # nwm
    total = vzorec_total.search(blok).groupdict()
    total_chapters = int(total['Total_chapters'])

    if total['NaNt']:
        total_words = -1
    else:
        total_words = float(total['Total_words'])
        if total['Total_K']:
            total_words *= 1000
        if total['Total_M']:
            total_words *= 1000000
        total_words = int(total_words)

    # če se fic na novo začne še nima updatov
    update = vzorec_update.search(blok)
    if update:
        update = update.groupdict()
        update_chapters = int(update['Update_chapters'])
        update_words = float(update['Update_words'])
        if update['Update_K']:
            update_words *= 1000
        update_words = int(update_words)
    else:
        update_chapters = total_chapters
        update_words = total_words

    datum_novega_poglavja = vzorec_date_updated.search(blok).groupdict()
    date_updated = datum_novega_poglavja['Date_updated']

    datum_prve_objave = vzorec_date_created.search(blok)
    if datum_prve_objave:
        datum_prve_objave = datum_prve_objave.groupdict()
        date_created = datum_prve_objave['Date_created']
    else:
        date_created = 'unknown'

    strani = vzorec_vseh_strani.search(blok)
    if strani:
        strani = strani.group('Strani')
        seznam_strani = izloci_strani(strani)
    else:
        # poiscemo ce kaj najdemo
        seznam_strani = []
        if re.compile(r'spacebattles').search(blok):
            seznam_strani.append('SB')
        elif re.compile(r'archiveofourown').search(blok):
            seznam_strani.append('AO3')
        elif re.compile(r'fanfiction').search(blok):
            seznam_strani.append('FF')
        elif re.compile(r'sufficientvelocity').search(blok):
            seznam_strani.append('SV')
        elif re.compile(r'questionablequesting').search(blok):
            seznam_strani.append('QQ')
        else:
            seznam_strani.append('Other')

    podatki = {
        'naslov': naslov,
        'avtor': author,
        '# novih poglavij': update_chapters,
        '# novih besed': update_words,
        '# poglavij': total_chapters,
        '# besed': total_words,
        'datum objave novega poglavja': date_updated,
        'datum prve objave': date_created,
        'seznam strani na katerih je fic': seznam_strani,
        'teden v katerem je bilo objavljeno novo poglavje': teden,
        'je quest': quest,
        'je zaključen': complete
    }

    return podatki

def obdelaj_teden(teden):
    '''Naredi slovar podatkov za vsak fic v tednu:
    (
    naslov,
    avtor,
    # novih poglavij,
    # novih besed,
    # poglavij,
    # besed,
    datum objave novega poglavja,
    datum prve objave,
    seznam strani na katerih je fic,
    teden v katerem je bilo objavljeno novo poglavje,
    je quest,
    je zaključen
    )'''

    teden_datoteka = datoteka_tedna(teden)
    vsebina = vsebina_datoteke(teden_datoteka)

    #vzorec, quest, complete
    seznam_superblokov = [
        (vzorec_New_Fics, False, False),
        (vzorec_New_Quests, True, False),
        (vzorec_Completed_Fics, False, True),
        (vzorec_One_shot_Fics, False, True),
        (vzorec_Revived_Fics, False, False),
        (vzorec_Revived_Quests, True, False),
        (vzorec_Updated_Fics, False, False),
        (vzorec_Updated_Quests, True, False)
    ]

    seznam = []
    for vzorec, quest, complete in seznam_superblokov:
        superblok = vzorec.search(vsebina)
        # ker včasih ni npr completed ficsov
        if superblok:
            for blok in vzorec_bloka.finditer(superblok.group(0)):
                podatki = izloci_podatke_fic(blok.group(0), teden, quest, complete)
                seznam.append(podatki)
    return seznam

def obdelaj_podatke(kazalo):
    '''naredi 3 sezname:
    seznam vseh različnih ficov, in njihovih podatkov
    seznam ficov po tednih
    seznam naslov - stran
    '''
    # opomba: izkaže se, da sta prva 2 tedna tako drugačna od ostalih, da ju ta program ne more obdelati
    # opomba: Del tega (slovar_vseh_ficov) deluje ker gremo od najnovejše proti najstarejši. Za izboljšavo bi lahko dodal da primerja datume
    seznam_po_tednih = []
    seznam_strani = []
    slovar_vseh_ficov = dict()
    for teden in seznam_tednov(kazalo):
        seznam_slovarjev_ficov = obdelaj_teden(teden)
        for slovar_fica in seznam_slovarjev_ficov:
            naslov_fica = slovar_fica['naslov']
            if naslov_fica not in slovar_vseh_ficov:
                seznam_strani_za_fic = slovar_fica.pop('seznam strani na katerih je fic')
                slovar_vseh_ficov[naslov_fica] = slovar_fica
            naslov_fica = slovar_fica.get('naslov')
            slovar_fica.pop('seznam strani na katerih je fic', None)
            for stran in seznam_strani_za_fic:
                seznam_strani += [{'naslov': naslov_fica, 'stran na kateri je fic': stran}]
        seznam_po_tednih += seznam_slovarjev_ficov

    return slovar_vseh_ficov.values(), seznam_po_tednih, seznam_strani

podatki_vseh_ficov, podatki_po_tednih, podatki_strani = obdelaj_podatke(kazalo)

zapisi_csv(podatki_vseh_ficov,
           ['naslov',
            'avtor',
            '# novih poglavij',
            '# novih besed',
            '# poglavij',
            '# besed',
            'datum objave novega poglavja',
            'datum prve objave',
            'teden v katerem je bilo objavljeno novo poglavje',
            'je quest',
            'je zaključen'
            ],
           os.getcwd() + "\\obdelani_podatki\\podatki_vseh_ficov.csv")

zapisi_csv(podatki_po_tednih,
           ['naslov',
            'avtor',
            '# novih poglavij',
            '# novih besed',
            '# poglavij',
            '# besed',
            'datum objave novega poglavja',
            'datum prve objave',
            'teden v katerem je bilo objavljeno novo poglavje',
            'je quest',
            'je zaključen'
            ],
           os.getcwd() + "\\obdelani_podatki\\podatki_po_tednih.csv")

zapisi_csv(podatki_strani,
           ['naslov',
            'stran na kateri je fic'
            ],
           os.getcwd() + "\\obdelani_podatki\\podatki_strani.csv")