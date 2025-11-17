#!/usr/local/bin/python3

from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
import requests
import subprocess
import os
from datetime import datetime

url = "https://cloud.urbi.it/urbi/progs/urp/ur1ME002.sto"
params = {
    'DB_NAME': 'n1200674',
    'w3cbt': 'S',
    'StwEvent': '9100030',
    'ElencoPubblicazioni_DimensionePagina': '500',
    'ElencoPubblicazioni_PaginaCorrente': '1'
}

data = {
    'idTreeView1': 'TreeView_Id',
    'Tipologia': '',
    'EnteMittente': '',
    'DaData': '',
    'AData': '',
    'Oggetto': '',
    'RifAttoAnno': '',
    'RifAttoNumero': '',
    'OpenTree': '1',
    'OpenTreeText': 'CATALOGO DOCUMENTI',
    'Archivio': '',
    'UR1ME001BT_CHIAMANTE': 'UR1ME002',
    'SOLCollegamentoAtti': '',
    'catnome': '',
    'caturl': '',
    'servnome': '',
    'BootstrapItalia_Home': '/urbi/bootstrap-italia/2.3.8',
    'Stepper_Idx': '1',
    'Collapse_Idx': '1',
    'Contenitore_Idx': '1',
    'TreeView_Idx': '1',
    'Form_Idx': '1',
    'Stepper_StepAttivo': '1',
    'Stepper_StepAttivoNome': '',
    'Stepper_NextStep': '2',
    'Stepper_NextStepNome': ''
}

response = requests.post(url, params=params, data=data)

if response.status_code == 200:
    with open("response.html", "w") as file:
        file.write(response.text)
else:
    print(f"Errore: {response.status_code}")


def generate_rss_feed(response):
    soup = BeautifulSoup(response.text, 'html.parser')

    feed = FeedGenerator()
    feed.title('Albo Pretorio - Comune di Soriano nel Cimino')
    feed.link(
        href='https://raw.githubusercontent.com/alexb-1983/myrss/refs/heads/master/albo_pretorio_feed.rss',
        rel='self',
        type="application/rss+xml"
    )
    feed.description(
        'Feed RSS degli ultimi documenti pubblicati sull’Albo Pretorio del Comune di Soriano nel Cimino'
    )

    rows = soup.find('tbody').find_all('tr')

    for row in rows:
        cols = row.find_all('td')

        strong_tags = cols[1].find_all('strong')
        if len(strong_tags) > 2:
            titolo = strong_tags[2].text.strip()
        else:
            titolo = "Titolo non trovato"

        button_url = cols[2].find('button').get('data-w3cbt-button-modale-url')
        link = f"https://cloud.urbi.it/urbi/progs/urp/{button_url}&DB_NAME=n1200674&w3cbt=S"

        descrizione_parziale = cols[1].text.strip()
        descrizione = (
            descrizione_parziale
            .replace(titolo, "")
            .replace("Pubblicazione", "")
            .strip()
        )

        entry = feed.add_entry()
        entry.title(titolo)
        entry.link(href=link)
        entry.description(descrizione)
        entry.guid(link)

    return feed


feed = generate_rss_feed(response)

output_file = 'albo_pretorio_feed.rss'
feed.rss_file(output_file)
print(f"Il file RSS è stato aggiornato: {output_file}")

# --- Commit & Push su GitHub ---
# Ottieni la data e ora corrente nel formato richiesto
now = datetime.now()
timestamp = now.strftime("%d-%m-%YT%H:%M:%S")

# Messaggio di commit
commit_message = f"Aggiornamento feed {timestamp}"

# Leggi il token dalla variabile d'ambiente
github_token = os.environ.get("GITHUB_TOKEN")
if not github_token:
    raise ValueError("La variabile GITHUB_TOKEN non è settata")

# URL con token
repo_url = f"https://{github_token}@github.com/alexb-1983/myrss.git"

# Esegui git add, commit e push
subprocess.run(["git", "add", output_file], check=True)
subprocess.run(["git", "commit", "-m", commit_message], check=True)
subprocess.run(["git", "push", repo_url], check=True)
