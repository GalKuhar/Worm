import os
import sys
import requests
import re

# ------ kopirano od profesorja ------

def pripravi_imenik(ime_datoteke):
    '''Če še ne obstaja, pripravi prazen imenik za dano datoteko.'''
    imenik = os.path.dirname(ime_datoteke)
    if imenik:
        os.makedirs(imenik, exist_ok=True)

def shrani_spletno_stran(url, ime_datoteke, vsili_prenos=False):
    '''Vsebino strani na danem naslovu shrani v datoteko z danim imenom.'''
    try:
        print('Shranjujem {} ...'.format(url), end='')
        sys.stdout.flush()
        if os.path.isfile(ime_datoteke) and not vsili_prenos:
            print('shranjeno že od prej!')
            return
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('stran ne obstaja!')
    else:
        pripravi_imenik(ime_datoteke)
        with open(ime_datoteke, 'w', encoding='utf-8') as datoteka:
            datoteka.write(r.text)
            print('shranjeno!')

def vsebina_datoteke(ime_datoteke):
    '''Vrne niz z vsebino datoteke z danim imenom.'''
    with open(ime_datoteke, encoding='utf-8') as datoteka:
        return datoteka.read()

# ------ moja koda ------

# downloada strani ki joh bom obdelal
# kazalo in letna porocila shrani zraven Zajem.py
# tedenska porocila shrani v mapo podatki

naslov_kazala = "https://shared.by.re-becca.org/misc/worm/"
kazalo = os.getcwd() + "\\podatki\\kazalo.html"

def shrani_kazalo(naslov_kazala):
    shrani_spletno_stran(naslov_kazala, "kazalo.html")

vzorec_teden = re.compile(
    r'\<a href=\"(?P<Teden>\d+-\d+-\d+\.html)\"'
)

vzorec_leto = re.compile(
    r'\<a href=\"(?P<Leto>\d+\.html)\"'
)

def shrani_strani_s_kazala(kazalo):
    vsebina_kazala = vsebina_datoteke(kazalo)

    # tu bi lahko dodatno naredili mapo, vendar to naredi že shrani_spletno_stran()
    for ujemanje in vzorec_teden.finditer(vsebina_kazala):
        shrani_spletno_stran(naslov_kazala + ujemanje.group('Teden'), os.getcwd() + "\\podatki\\" + ujemanje.group('Teden'))

    # letna porocila so malo drugacna, zato se shranjujejo posebej
    for ujemanje in vzorec_leto.finditer(vsebina_kazala):
        shrani_spletno_stran(naslov_kazala + ujemanje.group('Leto'), os.getcwd() + "\\podatki\\" +ujemanje.group('Leto'))

shrani_spletno_stran(naslov_kazala, kazalo)
shrani_strani_s_kazala(kazalo)