# Unsplash Daily Wallpaper Changer

Ein Python-Script, das täglich ein zufälliges Bild von Unsplash herunterlädt und als Hintergrundbild einrichtet.

## Features

- Lädt täglich automatisch ein neues Bild von Unsplash
- Unterstützt GNOME, KDE Plasma, XFCE und feh (für i3, bspwm, etc.)
- Konfigurierbare Bildkategorien und Ausrichtung
- Speichert Metadaten zum aktuellen Hintergrundbild

## Voraussetzungen

- Python 3.6 oder höher
- Unsplash API Access Key (kostenlos)
- Linux mit einer der unterstützten Desktop-Umgebungen

## Installation

### 1. Unsplash API Key erhalten

1. Gehe zu https://unsplash.com/developers
2. Erstelle einen Account oder melde dich an
3. Erstelle eine neue Applikation
4. Kopiere deinen Access Key

### 2. Dependencies installieren

```bash
pip install -r requirements.txt
```

Oder systemweit:

```bash
pip3 install requests
```

### 3. API Key konfigurieren

Erstelle eine `.env` Datei:

```bash
cp .env.example .env
```

Bearbeite `.env` und trage deinen API Key ein:

```
UNSPLASH_ACCESS_KEY=dein_echter_api_key
```

### 4. Script testen

Teste das Script manuell:

```bash
python3 change_wallpaper.py
```

Das Script lädt die `.env` Datei automatisch - keine Umgebungsvariablen nötig!

## Automatische tägliche Ausführung

### Option 1: Systemd Timer (empfohlen)

**Hinweis:** Da das Script die `.env` Datei automatisch lädt, brauchst du den API Key nicht in der Service-Datei einzutragen. Du kannst die Dateien direkt verwenden.

1. Kopiere die Service-Dateien:

```bash
mkdir -p ~/.config/systemd/user/
cp wallpaper-changer.service ~/.config/systemd/user/
cp wallpaper-changer.timer ~/.config/systemd/user/
```

2. Aktiviere und starte den Timer:

```bash
systemctl --user enable wallpaper-changer.timer
systemctl --user start wallpaper-changer.timer
```

3. Überprüfe den Status:

```bash
systemctl --user status wallpaper-changer.timer
systemctl --user list-timers
```

4. Manuell ausführen zum Testen:

```bash
systemctl --user start wallpaper-changer.service
```

### Option 2: Cron

Öffne den Crontab Editor:

```bash
crontab -e
```

Füge folgende Zeile hinzu (läuft täglich um 9:00 Uhr):

```
0 9 * * * /usr/bin/python3 /home/dein_benutzer/projekte/background-changer/change_wallpaper.py
```

Das Script lädt die `.env` Datei automatisch, keine Umgebungsvariablen nötig.

## Konfiguration

Du kannst das Script anpassen, indem du folgende Variablen in `change_wallpaper.py` änderst:

```python
# Bildkategorien (Komma-getrennt)
QUERY = 'nature,landscape'

# Ausrichtung: 'landscape', 'portrait', oder 'squarish'
ORIENTATION = 'landscape'

# Speicherort
WALLPAPER_DIR = Path.home() / '.local' / 'share' / 'wallpapers'
```

### Beliebte Kategorien

- `nature` - Natur
- `landscape` - Landschaften
- `architecture` - Architektur
- `minimal` - Minimalistisch
- `space` - Weltraum
- `animals` - Tiere
- `city` - Städte

## Desktop-Umgebungen

Das Script unterstützt automatisch:

- **GNOME/Ubuntu**: Verwendet `gsettings`
- **KDE Plasma**: Verwendet `qdbus`
- **XFCE**: Verwendet `xfconf-query`
- **i3/bspwm/andere**: Verwendet `feh` als Fallback

## Gespeicherte Dateien

- Aktuelles Hintergrundbild: `~/.local/share/wallpapers/current_wallpaper.jpg`
- Metadaten: `~/.local/share/wallpapers/metadata.txt`

## Troubleshooting

### "UNSPLASH_ACCESS_KEY nicht gesetzt"

Stelle sicher, dass die `.env` Datei im Projektverzeichnis existiert und deinen API Key enthält:

```bash
cp .env.example .env
# Bearbeite .env und trage deinen API Key ein
```

### Hintergrundbild wird nicht gesetzt

Überprüfe, ob die benötigten Tools installiert sind:

- GNOME: `gsettings` sollte vorhanden sein
- KDE: `qdbus` sollte vorhanden sein
- XFCE: `xfconf-query` sollte vorhanden sein
- Fallback: Installiere `feh` mit `sudo apt install feh`

### Systemd Service funktioniert nicht

Logs anzeigen:

```bash
journalctl --user -u wallpaper-changer.service
```

## Lizenz

MIT License - Frei verwendbar für private und kommerzielle Zwecke.

## Credits

Bilder von [Unsplash](https://unsplash.com) - Kostenlose hochqualitative Fotos.
