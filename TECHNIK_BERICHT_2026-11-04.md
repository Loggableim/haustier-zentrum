# Technikprüfung Haustierzentrum — 4. November 2026 (UTC)

## Ergebnis

Kein Push und kein Deploy. Merles QA-Freigabe fehlt (vorheriger Auftrag scheiterte an der Anmeldung). Zusätzlich sind CMP, interne 404-Ziele und SEO-Reste offen. Die lokale Technikvorbereitung ist geprüft.

Projekt: /data/.openmausbot/workspaces/0db8a3b8-29fb-4aad-a052-03749785958e/haustier-zentrum; Ausgangscommit 5f51bfe, Branch main. Der Ordner war erreichbar und anfangs sauber.

## Live geprüft

- https://haustierzentrum.com/: erreichbar; alle 125 Artikel aus der Sitemap ebenfalls HTTP 200, mit genau passender Canonical-URL.
- /sitemap.xml: HTTP 200, sitemapindex mit genau zwei locs auf /sitemap-articles.xml und /sitemap-static.xml. Artikeldatei: 125 eindeutige URLs; statische Datei: vier URLs (Start, About, Impressum, Datenschutz).
- /robots.txt: HTTP 200, Crawling erlaubt, korrekter Sitemap-Verweis.
- /ads.txt: HTTP 200; `google.com, pub-9094916118868532, DIRECT, f08c47fec0942fa0`. Publisher-ID stimmt mit den eingebundenen Anzeigen-Skripten überein. Kontoinhaberschaft und AdSense-Freischaltung nicht geprüft.
- /impressum und /datenschutz: HTTP 200, Navigation/Footer auf der Startseite verlinken beide. Das Vorhandensein ist bestätigt; keine vollständige Rechtsprüfung.
- /tarek-pruefung-404-20261104: echte HTTP-404-Antwort, eigene Fehlerseite, kein Soft-404.
- Alle 59 unten aufgeführten unterschiedlichen fehlerhaften Linkziele wurden zusätzlich live abgerufen: ausnahmslos HTTP 404.

## AdSense und sensible Dateien — offen / kritisch

1. Startseite lädt adsbygoogle.js direkt bei cookieConsent=null. Im Browser ist __tcfapi nicht definiert. Auch artikel/vogelkaefig-voliere-kaufen-vergleich-2026.html enthält ein unbedingtes AdSense-Skript. Die übrigen Stichproben nutzen ein eigenes localStorage-Opt-in; das belegt keine zertifizierte CMP. In keinem der 125 lokalen Artikel wurden __tcfapi/fundingchoices/googlefc gefunden. Eine möglicherweise extern im Konto konfigurierte CMP wurde nicht im AdSense-Konto geprüft.
2. Google verlangt für personalisierte Anzeigen in EWR, UK und Schweiz eine zertifizierte CMP mit TCF-Integration. Quelle, am Prüftag abgerufen: https://support.google.com/adsense/answer/13554116?hl=en . Das eigene Akzeptieren/Ablehnen-Banner genügt als Nachweis dafür nicht. Vor Freigabe CMP im Publisher-Konto einrichten und Einwilligung, Ablehnung sowie Widerruf im Browser prüfen. Diese Konfiguration wurde nicht vorgenommen.
3. /_minimax_key.py liefert live HTTP 200 (application/octet-stream). Dateiinhalte und Schlüssel wurden nicht ausgegeben; ob dort ein gültiger Schlüssel steht, ist nicht bewertet. Die bisherige CI deployt das ganze Repository. Das ist ein kritischer Auslieferungsfehler. /.git/config liefert dagegen 404. Weitere sensible URLs wurden nicht systematisch abgerufen.
4. _get_key.py, _minimax_key.py und der bereits getrackte Bytecode wurden lokal aus dem Git-Index entfernt und ignoriert; lokale Dateien bleiben erhalten. Die öffentliche Git-Historie und der bisherige Live-Deploy bleiben bis zu weiteren Maßnahmen unverändert. Etwaige dort enthaltene Zugangsdaten müssen beim Anbieter geprüft und gegebenenfalls rotiert werden; eine Rotation ist nicht erfolgt.
5. Keine vollständige Inhalts-/AdSense-Richtlinienfreigabe: Lina und Merle haben ihre Pakete laut Rückmeldung noch nicht ausgeführt. Medizinische Aussagen, Bilder und inhaltliche Qualitätsfragen sind damit weiterhin ungeprüft.

## Lokale SEO-Prüfung (125 Artikel)

- 4899 interne Linkvorkommen geprüft: 60 fehlerhafte Vorkommen, 59 unterschiedliche Ziele, 13 Quelldateien. Fragmente/Anker wurden nicht geprüft.
- Canonicals: 125/125 korrekt. Kein hreflang vorhanden; für die ausschließlich deutsche Ausgabe ist keine künstliche Mehrsprachigkeitsauszeichnung ergänzt worden.
- JSON-LD: alle vorhandenen Blöcke syntaktisch parsebar. 112 Seiten mit BlogPosting, sechs mit Article, 71 mit FAQPage, sechs mit BreadcrumbList. Dies ist keine Bestätigung durch Googles Rich Results Test und kein Abgleich sämtlicher Schema-Inhalte mit sichtbarem Text.
- Sieben Seiten ohne Article-/BlogPosting-Schema:
  - artikel/allergien-bei-hund-und-katze-2026-umwelt-futter-und-fell-ganzheitliche-strategie.html
  - artikel/ganzheitliche-hundegesundheit-2026-wie-sie-krankheiten-fruehzeitig-erkennen-und-.html
  - artikel/hundeerziehung-neu-gedacht-2026-warum-klassisches-gehorsamstraining-an-modernen-.html
  - artikel/katzen.html
  - artikel/naehrstoff-kompass-2026-so-waehlen-sie-das-richtige-futter-fuer-hund-katze-und-k.html
  - artikel/notfall-checkliste-2026-erste-hilfe-fuer-hund-katze-und-kleintier-was-jede-halte.html
  - artikel/stille-signale-erkennen-wie-hunde-und-katzen-schmerzen-zeigen-und-was-halter-202.html
- H1-Prüfung: artikel/aquarium-einrichtung.html hat nicht genau ein H1. Fehlende Breadcrumb-Auszeichnung auf 119 Seiten bleibt offen; FAQ-Schema nur bei tatsächlich passendem sichtbarem FAQ ergänzen.

## Technische Änderungen

- .deploy.sh verweist portabel auf deploy.sh; beide enthalten keinen festen Windows-Pfad mehr.
- deploy.sh bereitet standardmäßig nur lokal vor, ohne git add -A, Commit, Rebase oder Push. --push verlangt main, einen sauberen Arbeitsbaum und QA_APPROVED_COMMIT passend zu HEAD. Dies ist eine Bedienungssperre: die tatsächliche Freigabe von Merle muss separat vorliegen, die Variable verifiziert keine Identität.
- _refresh_indexing.py und _generate_feed.py verwenden ihr eigenes Dateiverzeichnis. Sitemap-Daten werden zeitzonenfest gelesen; bei fehlendem Inhaltsdatum gilt der letzte Git-Commit der Datei statt des Checkout-Zeitpunkts. Falsche Zählung und irreführende Änderungsanzeige korrigiert.
- Sitemapdateien und RSS lokal regeneriert: zwei Teil-Sitemaps, 125 Artikel, vier statische Seiten, 40 RSS-Einträge. RSS war noch auf dem Stand Juni; nun aktuelle Artikeldaten, korrekt dekodierte HTML-Entities sowie vorhandene Bilddateien mit richtigem MIME-Typ und Dateigröße.
- _build_public.py validiert Sitemap-Struktur, Artikelabdeckung und RSS-URLs und erstellt dist/ aus einer Dateityp-/Verzeichnis-Positivliste. Python, Bytecode, Shell-Skripte, Datenbanken, interne Notizen, Git-Dateien und Key-Helfer kommen nicht in den Upload.
- .github/workflows/deploy.yml baut dist/ und deployt künftig dieses Verzeichnis, statt den Repository-Root.
- _audit_technical.py ist eine reproduzierbare, nur lesende Prüfung; Details in TECHNIK_AUDIT_2026-11-04.json.

## Deployweg und Verifikation

Bestätigter Weg: Push auf main → .github/workflows/deploy.yml → GitHub Actions → npx wrangler pages deploy → Cloudflare Pages-Projekt haustier-zentrum. Der zuletzt vorhandene Lauf 72 war erfolgreich und gehört zu Ausgangscommit 5f51bfe:
https://github.com/Loggableim/haustier-zentrum/actions/runs/35479761395

Der geänderte Workflow wurde nicht auf GitHub ausgeführt. Cloudflare-Kontoeinstellungen, Domain-Zuordnung und zusätzliche Deploymechanismen sind nicht vollständig geprüft.

Lokal ausgeführt:
```sh
PYTHON=/tmp/tarek-python/usr/bin/python3.11 bash deploy.sh --prepare
/tmp/tarek-python/usr/bin/python3.11 _audit_technical.py
/tmp/tarek-python/usr/bin/python3.11 _generate_feed.py
/tmp/tarek-python/usr/bin/python3.11 _build_public.py
bash -n deploy.sh .deploy.sh
git diff --check
```
Das System enthielt kein Python. Für die Prüfung wurde Python 3.11 aus Debian-Paketen ausschließlich unter /tmp/tarek-python entpackt; keine Systeminstallation. In CI wird Python 3.12 eingerichtet.

Erfolgreich: Dry-Runs und echte Generierung, XML-Parsing, 40 RSS-Einträge, Bildpfade/-größen, Entity-Escaping, Python-Kompilierung, Shell-Syntax, Whitespace-Prüfung, 125 Artikel im Build ohne interne Dateien. Negativprüfung: ungültiger Sitemapindex wird abgelehnt. --push ohne QA_APPROVED_COMMIT bricht vor jedem Push erwartungsgemäß ab.

## Interne 404-Ziele nach Quelldatei

### artikel/aquarium-pflanzen-einsteiger.html

- `/aquarium-bodengrund-wahl`
- `/aquarium-wasserwechsel-anleitung`
- `/aquarium-einsteiger-guide`

### artikel/chinchilla-ernaehrung-futter.html

- `/kleintiere`
- `/kleintiere/chinchilla-haltung`
- `/kleintiere/chinchilla-kaefig-einrichten`
- `/kleintiere/beschäftigung-kleintiere`

### artikel/dog-sitting-hundesitter-finden.html

- `/hunde/hundeerziehung-grundlagen`
- `/hunde/hundefutter-ratgeber`
- `/hunde/hundespielzeug`
- `/hunde/hundegesundheit-vorsorge`
- `/hunde/hundegeschirr`

### artikel/hamster-ernaehrung-futterplan.html

- `/kleintiere/hamster/hamsterratten-ratgeber`
- `/kleintiere/hamster/goldhamster-vs-zwerghamster`
- `/kleintiere/hamster/hamster-krankheiten-erkennen`

### artikel/hundeangst-training-tipps.html

- `/hunde/erziehung/silvester-mit-hund`
- `/hunde/erziehung/welpen-erziehung`
- `/hunde/gesundheit/hundestress-erkennen`
- `/hunde/erziehung/hund-bleibt-allein`
- `/hunde/erziehung/hundeschule-tipps`
- `/hunde/erziehung/silvester-mit-hund`
- `/hunde/erziehung/ruhiges-spazierengehen`

### artikel/hundefutter-vergleich-2026.html

- `/trockenfutter-vs-nassfutter-hund/`
- `/barfen-hund-anleitung/`
- `/welpenfutter-empfehlung/`
- `/hunde-snacks-gesund/`
- `/futtermittelunvertraeglichkeit-hund/`

### artikel/katzen-kratzmoebel-test.html

- `/katzen/katzenerziehung/`
- `/katzen/katzengerechte-wohnung/`
- `/katzen/zubehoer/`
- `/katzen/spiel-und-beschaeftigung/`

### artikel/katzen-zimmerpflanzen-giftig.html

- `/katzen/erste-hilfe-katze`
- `/katzen/gesundheit`
- `/katzen/tierarzt-kosten`
- `/katzen/transportbox`
- `/katzen/katzenbalkon-gestaltung`
- `/katzen/tierkrankenversicherung`

### artikel/katzenfreundliche-wohnung-gestalten.html

- `/mehrkatzenhaushalt-harmonisch-gestalten`
- `/katze-kratzt-moebel-was-tun`
- `/ungefaehrliche-pflanzen-fuer-katzen`
- `/katzen-mit-nierenerkrankung-richtig-fuettern`
- `/wohnungshaltung-katze-tipps`

### artikel/katzenrassen-vergleich.html

- `/kategorie/hunde.html`
- `/kategorie/kleintiere.html`

### artikel/vogelvoliere-kaufen-checkliste.html

- `/wellensittich-haltung/`
- `/kanarienvogel-pflege/`
- `/papageien-als-haustiere/`
- `/voegel/voegelfutter-grundlagen/`
- `/voegel/erstausstattung-voegel/`

### artikel/welpenschule-finden-kosten.html

- `https://haustierzentrum.com/hunde/welpen/welpenerziehung-tipps`
- `https://haustierzentrum.com/hunde/welpen/welpenspielgruppe`
- `https://haustierzentrum.com/hunde/welpen/ersthund-welpen`
- `https://haustierzentrum.com/hunde/welpen/positive-verstaerkung`
- `https://haustierzentrum.com/hunde/welpen/konsequenz-bei-der-erziehung`

### artikel/whippet-rasseguide.html

- `/hunde/hund-und-kind`
- `/hunde/hundemantel-groessen`
- `/hunde/zweiter-hund-einziehen`
- `/hunde/welpenerziehung-tipps`
- `/hunde/barf-fuer-hunde-einstieg`
- `/hunde/erstausstattung-hund`

Keine stillen Umleitungen auf nur ungefähr passende Themen angelegt. Die Linkliste bleibt zur inhaltlich passenden Korrektur mit Lina offen.
