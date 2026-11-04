# Technik-Folgepaket — 4. November 2026

Projekt: `/data/.openmausbot/workspaces/0db8a3b8-29fb-4aad-a052-03749785958e/haustier-zentrum`
Ausgangscommit: `0e3dfb6`, Branch `main`. Nur lokale Änderungen, kein Push und kein Deploy.

## Links

Alle 60 gemeldeten fehlerhaften Linkvorkommen in den 13 Quelldateien bearbeitet: 40 auf bestehende passende Artikel umgestellt, 20 Links entfernt und sichtbaren Text erhalten. Keine künstlichen Redirects. Jede Änderung steht in `TECHNIK_LINKFIX_2026-11-04.json` (Quelle, altes Ziel, neues Ziel bzw. null für entfernten Link).

Erneuter lokaler Check: 125 Artikel, 4856 interne Linkvorkommen, **0 fehlende interne Ziele**. Der Check bildet Cloudflare-Pages-Dateiauflösung mit und ohne `.html` ab. Ankerfragmente sind nicht geprüft. Die Änderung ist noch nicht live; die früher bestätigten Live-404-Links verschwinden erst nach einem freigegebenen Deploy.

## Gemeinsame Werbe-Einwilligung

`js/consent.js` ist der einzige AdSense-Lader. Alle 125 Artikel und die Startseite binden ihn genau einmal mit `defer` ein; die vollständigen statischen HTML-Seiten ebenfalls.

- Vor ausdrücklicher Zustimmung: kein AdSense-Skript, kein Ad-Slot, keine Werbe-Preconnects und keine Nachlade-Injektion. 303 nicht zu Amazon gehörende Werbeplatzhalter sind entfernt. Zwei manuelle Slots mit erfundener Platzhalter-ID `1234567890` sind entfernt. Nach Zustimmung wird nur der Auto-Ads-Lader des vorhandenen Publishers eingefügt, einmal je Seite.
- „Werbung akzeptieren“ / „Ablehnen / Einwilligung widerrufen“; „Werbe-Einstellungen“ auf jeder Seite dauerhaft erreichbar. Bei Widerruf nach bereits ausgeführtem Werbeskript wird die Seite sofort mit gespeichertem Nein neu geladen. Andere offene Fenster reagieren auf geänderte/gelöschte Einstellungen.
- Neuer Speicherschlüssel `cookieConsentV2`; alte pauschale `cookieConsent=accepted`-Werte gelten nicht als neue ausdrückliche Einwilligung. Bei gesperrtem Speicher bleibt Werbung zunächst aus; eine Wahl gilt dann nur für die aktuelle Seite. Datenschutzseite benennt den neuen Schlüssel.
- Keine zertifizierte CMP implementiert oder nachgewiesen. Der technische Opt-in ersetzt deren Einrichtung durch Cid nicht. Tatsächliche Auslieferung von Auto Ads und Kontokonfiguration sind ungeprüft.

## Schema und beschädigte Dokumente

Sieben bisher schemafreie Artikel haben jetzt minimales Article-JSON-LD aus vorhandenen Titeln, Beschreibungen und Canonicals, mit Sprache `de`; keine erfundenen Autoren, Daten, Studien oder Bewertungen. Vorhandene FAQ-/ItemList-/Breadcrumb-Daten bleiben erhalten; keine künstlichen Breadcrumbs ergänzt. Vollständige Dateiliste: `missing_article_schema` im Ausgangsbericht `TECHNIK_AUDIT_2026-11-04.json`.

`artikel/aquarium-einrichtung.html` war nach dem JSON-LD abgeschnitten und hatte überhaupt keinen Body. Den vollständigen sichtbaren Artikel einschließlich H1, Layout und Navigation aus Git-Commit `0ba211d` wiederhergestellt; aktuellen Head behalten, Datenschutzlink ergänzt. Keine Neufassung des Inhalts. Eine redaktionelle Neubewertung dieses älteren Inhalts ist weiterhin offen.

Zusatzbefund: `artikel/britisch-kurzhaar-rasseguide.html` endete mitten in einer SVG-Grafik des Related-Bereichs mit wörtlichem „(truncated)“. Den abgeschnittenen Related-Bereich entfernt und Main, Footer, Body und HTML sauber abgeschlossen; Artikeltext erhalten. Damit funktioniert der gemeinsame Einwilligungsmechanismus auch dort.

Ergebnis über 125 Artikel: **0 H1-Fehler, 0 fehlende Article-/BlogPosting-Daten, 0 JSON-LD-Parsefehler, 0 Canonical-Fehler**. Keine Rich-Results-Zertifizierung oder vollständige Schema-Inhaltsprüfung.

## Build und reproduzierbare Prüfung

`_build_public.py` kopiert jetzt auch ausschließlich `.js`-Dateien aus `js/`. `deploy.sh` und `.github/workflows/deploy.yml` prüfen den fertigen Build mit `_check_release.py dist`; CI führt zusätzlich die sieben Laufzeittests aus `_test_consent.cjs` aus. Der Preflight bricht bei alten Werbeladern, fehlender/doppelter Einwilligungsdatei, Slots/Platzhaltern sowie den geprüften Link-/Schema-/H1-Fehlern ab.

Ausgeführt:

```sh
PYTHON=/tmp/tarek-python/usr/bin/python3.11 bash deploy.sh --prepare
/tmp/tarek-python/usr/bin/python3.11 _check_release.py dist
node _test_consent.cjs
bash -n deploy.sh .deploy.sh
git diff --check
```

Prüfausgabe:

```text
dist: 125 articles, 4856 internal links, 0 broken targets
dist: 126 pages, 0 inline AdSense loaders/slots, exactly 1 shared consent loader/page
dist: 0 missing Article/BlogPosting schemas, 0 JSON-LD/H1/canonical errors
7 consent runtime tests passed
```

Zusätzlich bestanden: Syntaxprüfung aller 201 nichtleeren Inline-JavaScript-Blöcke der Startseite/Artikel, Python-Syntax der Prüfer/Builder, Negativprüfung mit absichtlich unbedingtem AdSense-Skript (erwartet abgelehnt und Testdatei anschließend wiederhergestellt). Öffentlicher Build enthält keine `.py`, `.pyc` oder `.sh`. Sitemaps: zwei Teil-Sitemaps, 125 Artikel und vier statische Seiten; RSS: 40 Einträge. `dist/` ist neu gebaut, bleibt bewusst unversioniert.

Im eingebauten Browser wurde der lokale Aquarium-HTML-Stand als Vorschau gerendert: genau ein H1, sichtbarer vollständiger Artikel. Gemeinsamen Consent-Code im echten DOM geprüft: vor Zustimmung 0 AdSense-Skripte/0 Slots, nach Zustimmung genau ein abgefangener Ladeversuch, Banner geschlossen, Einstellungen wieder geöffnet und Widerruf erreichbar. Der Test hat keine Google-Werbung angefordert. Speicherung, Seitenwechsel, Reload-Aufruf beim Widerruf und Fensterwechsel wurden mit dem isolierten JavaScript-Laufzeittest geprüft, nicht mit einem Live-AdSense-Konto.

## Offen

Kein Push/Deploy. Merles Qualitätsfreigabe und zertifizierte CMP bleiben offen; Live-Auslieferung sensibler Dateien und Schlüsselrotation werden durch diesen lokalen Commit nicht behoben. Der bestehende Deployweg bleibt GitHub Actions → Wrangler → Cloudflare Pages. Der geänderte Workflow wurde noch nicht auf GitHub ausgeführt. Keine zugehörigen Automationen vorhanden.
