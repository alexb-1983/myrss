from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
import requests

url = "https://cloud.urbi.it/urbi/progs/urp/ur1ME002.sto"
params = {
    'DB_NAME': 'n1200674',
    'w3cbt': 'S',
    'StwEvent': '9100030',
    'ElencoPubblicazioni_DimensionePagina': '500',
    'ElencoPubblicazioni_PaginaCorrente': '1'
}

# Dati del form
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

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1"
}

# usa una sessione persistente per mantenere i cookie
s = requests.Session()
s.headers.update(headers)

# prima un GET per creare la sessione
s.get(url, params={"DB_NAME": "n1200674"}, timeout=10)

# poi la POST con tutti i parametri
response = s.post(url, params=params, data=data, timeout=15)

# Verifica la risposta
if response.status_code == 200:
    # Salva la risposta in un file
    with open("response.html", "w") as file:
        file.write(response.text)
else:
    print(f"Errore: {response.status_code}")


def generate_rss_feed(response):
    """Genera un feed RSS a partire dal contenuto HTML.

    Args:
        response: Il contenuto HTML della pagina.

    Returns:
        Un oggetto FeedGenerator contenente il feed RSS generato.
    """
    
    soup = BeautifulSoup(response.text, 'html.parser')  # Usa response.text per ottenere il corpo della risposta
    feed = FeedGenerator()
    feed.title('Albo Pretorio - Comune di Soriano nel Cimino')
    feed.link(href='https://raw.githubusercontent.com/alexb-1983/myrss/refs/heads/master/albo_pretorio_feed.rss', rel='self', type="application/rss+xml")
    feed.description('Feed RSS degli ultimi documenti pubblicati sull''Albo Pretorio del Comune di Soriano nel Cimino')

    rows = soup.find('tbody').find_all('tr')

    for row in rows:
        cols = row.find_all('td')

        # Estrai il titolo dalla seconda colonna (cerca il terzo <strong>)
        strong_tags = cols[1].find_all('strong')
        if len(strong_tags) > 2:
            titolo = strong_tags[2].text.strip()
        else:
            titolo = "Titolo non trovato"

        # Estrai il link dalla terza colonna del button
        button_url = cols[2].find('button').get('data-w3cbt-button-modale-url')
        link = f"https://cloud.urbi.it/urbi/progs/urp/{button_url}&DB_NAME=n1200674&w3cbt=S"
        
        # Estrai tutta la descrizione tranne il link
        descrizione_parziale = cols[1].text.strip()
        # Rimuovi solo il link e la parola 'Pubblicazione' (non il titolo)
        descrizione = descrizione_parziale.replace(titolo, "").replace("Pubblicazione", "").strip()

        # Crea un nuovo elemento del feed
        entry = feed.add_entry()
        entry.title(titolo)
        entry.link(href=link)
        entry.description(descrizione)
        entry.guid(f"{link}")
		
    return feed

# Genera il feed RSS
feed = generate_rss_feed(response)

# Sovrascrive il file albo_pretorio_feed.rss esistente
output_file = 'albo_pretorio_feed.rss'
feed.rss_file(output_file)
print(f"Il file RSS è stato aggiornato: {output_file}")


