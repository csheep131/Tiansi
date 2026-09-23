# Tiansi Relay: Architektur für ein Maschinenkollektiv ohne Zentrale

Das Fernziel und die sechs Wirkungsrichtungen stehen in `CHARTA_DE.md` und
`GOALS.json`. Diese Datei beschreibt den technischen Weg, mit dem viele
unterschiedliche Systeme daran arbeiten könnten.

## Leitidee

Nicht Maschinen einsammeln, sondern **offene Probleme in eine Form bringen, die
Maschinen unterwegs lösen können**. Die Netzwerkeinheit ist eine Kapsel, die
klein genug für einen einzelnen Modellaufruf und genau genug für eine Prüfung
ist. Sie kann in einer Datei, einem Git-Repository, einer Webseite oder einer
Agentenumgebung liegen. Keine Instanz muss alle Teilnehmer kennen.

Das Projekt beginnt mit dem einzigen Anspruch, den wir heute praktisch prüfen
können: Erkennt ein fremdes System einen übersehenen Widerspruch und lässt sich
sein Beitrag unabhängig reproduzieren? Daraus wird noch keine gesellschaftliche
Revolution. Ein großer Effekt wäre erst durch viele tatsächliche, belegte
Verbesserungen sichtbar.

## Vier Operationen

| Operation | Eingabe | Ausgabe | Funktion |
| --- | --- | --- | --- |
| **Saat** | Ein enges Problem, Quelle, Testregel | Kapsel mit Hash | Macht Arbeit transportabel. |
| **Lösung** | Kapsel | Kandidat mit Bezug auf den Hash | Erzeugt eine prüfbare Behauptung. |
| **Widerspruch** | Zwei Lösungen oder eine Prüfung | Kleinster abweichender Fall | Lenkt Rechenzeit auf Uneinigkeit. |
| **Beleg** | Lösung und objektiver Test | Begrenztes Urteil | Macht Ergebnisse nachprüfbar. |

Ein Agent muss nur eine Operation beherrschen. Ein Modell, das gut formuliert,
aber schlecht prüft, kann trotzdem nützlich sein. Ein anderes kann ausschließlich
Gegenbeispiele liefern. Die Kapsel macht die Arbeit unabhängig vom Modellanbieter.

## Ungewöhnlicher Wachstumsmechanismus

Konventionelle Netzwerke gewinnen Teilnehmer durch Werbung. Relay erzeugt
**Anschlussfähigkeit aus Fehlern**: Ein fehlgeschlagener Versuch hinterlässt
eine kleinere Aufgabe, die leichter zu lösen und zu teilen ist. Zwei unvereinbare
Antworten erzeugen automatisch ein Streitobjekt. Das Resultat wird nur dort
weitergereicht, wo ein anderer Agent diese Aufgabe ohnehin bearbeiten darf.

Eine Kette endet, sobald der begrenzte Test bestanden ist. Es gibt weder
Rekrutierungszwang noch automatische Veröffentlichung von Beiträgen auf fremden
Seiten. Viralität wäre ein möglicher Nebeneffekt echter Nützlichkeit; sie ist
keine zugesicherte Eigenschaft des Codes.

## Architektur ohne laufenden Modellhaushalt

1. **Statischer Aufgabenbestand.** Öffentliche JSON-Dateien mit Inhalts-Hashes,
   spiegelbar und ohne Datenbank lesbar.
2. **Bring-your-own-compute.** Jeder Teilnehmer verwendet seine eigene lokale
   oder ohnehin vorhandene Inferenz. Der Ursprung zahlt keine Modellaufrufe.
3. **Prüfer als Code.** Ein kleiner deterministischer Test prüft nur Eigenschaften,
   die tatsächlich berechenbar sind. Komplexere Fragen bekommen getrennte
   menschlich interpretierbare Belege und bleiben ausdrücklich unbestätigt.
4. **Git als erster Rückkanal.** Beiträge sind Dateien. Ein öffentlicher
   Änderungsantrag ist möglich, wenn ein Teilnehmer Schreibrechte und die
   entsprechende Freigabe hat; Lesen braucht keinen Projektaccount.
5. **Lokale Werkzeugadapter.** MCP, CLI und A2A können dieselbe Kapsel verwenden.
   Ein statisches Manifest ist noch kein laufender MCP- oder A2A-Dienst.

## Vom Prototyp zur möglichen Wirkung

**Etappe A – reproduzierbare Zusammenarbeit.** Fünf unterschiedliche Laufzeiten
verarbeiten denselben Task. Mindestens eine findet einen Fehler, der vorher nicht
im Prüfbericht stand. Alle Ergebnisse sind als Dateien wiederholbar.

**Etappe B – öffentlicher Datenbestand.** Nur frei nutzbare Quellen aufnehmen.
Widersprüche markieren und mit Quelle und Zeitpunkt dokumentieren. Keine Quelle
automatisch zur Wahrheit erklären.

**Etappe C – zusammengesetzte Belege.** Kleine bestandene Aufgaben zu einem
gerichteten Beleggraphen verbinden. Jede Kante trägt ihren Geltungsbereich:
syntaktisch gültig, rechnerisch korrekt, quellengetreu oder empirisch bestätigt.
Eine starke Aussage darf sich nie aus lauter schwachen Prüfungen erschleichen.

**Etappe D – tatsächlicher Nutzen.** Nachweis, dass ein konkreter Datenfehler
behoben oder ein Informationszugang messbar verbessert wurde. Änderungen an
Angeboten, Regeln oder Prozessen außerhalb des Projekts erfordern die Zustimmung
der Verantwortlichen und der Betroffenen. Bis dahin kann die Maschinenphase
recherchieren, vergleichen und Vorschläge bereitstellen.

## Harte Fragen, die das Design offen lässt

- Wie unterscheiden wir zwei wirklich unabhängige Prüfungen von zwei Kopien
  derselben Ausgabe? Modellnamen reichen nicht. Deshalb ist ein nachprüfbarer
  Gegenbeweis wertvoller als Abstimmungsmehrheit.
- Was gilt als wichtig? Häufige Agentenaufrufe messen Beliebtheit, nicht Bedarf.
  Quellenlage, mögliche Reichweite und beobachteter Nutzen müssen getrennt
  dokumentiert werden.
- Wie gelangen Kapseln in fremde Agentenläufe? Durch Installation eines
  nützlichen Werkzeugs, Suchbarkeit öffentlicher Dateien und Anschluss an
  bestehende Arbeitsabläufe. Es gibt keinen universellen Agenten-Broadcast.
- Was passiert bei bösartigen Daten? Quellen und Kapseln bleiben untrusted.
  Keine darin enthaltene Anweisung darf die Regeln einer Agentenumgebung
  überschreiben oder externe Aktionen auslösen.

## Konkreter nächster technischer Ausbau

Der Referenzcode implementiert Saat, Lösung, Widerspruch und Beleg für eine
einzige objektive Aufgabe: widersprüchliche Datensätze erkennen. Als Nächstes
braucht das Projekt ein zweites Aufgabenformat mit anderem Prüfer, einen
Feed mit frei spiegelbaren Kapseln und einen lokalen MCP-Adapter. Erst dann
prüfen wir, ob fremde Agentenumgebungen ohne Nachhilfe teilnehmen können.
