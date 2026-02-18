#!/usr/bin/env python3
"""
Unsplash Daily Wallpaper Changer
Lädt täglich ein zufälliges Bild von Unsplash herunter und setzt es als Hintergrundbild.
"""

import os
import requests
import subprocess
from pathlib import Path
from datetime import datetime

# Konfiguration
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', '')
WALLPAPER_DIR = Path.home() / '.local' / 'share' / 'wallpapers'
CURRENT_WALLPAPER = WALLPAPER_DIR / 'current_wallpaper.jpg'

# Unsplash API Konfiguration
UNSPLASH_API_URL = 'https://api.unsplash.com/photos/random'

# Optional: Kategorien für Bilder (kann angepasst werden)
# Beispiele: 'nature', 'landscape', 'architecture', 'minimal'
QUERY = 'nature,landscape'
ORIENTATION = 'landscape'  # 'landscape', 'portrait', oder 'squarish'


def setup_directories():
    """Erstellt das Wallpaper-Verzeichnis falls es nicht existiert."""
    WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Wallpaper-Verzeichnis: {WALLPAPER_DIR}")


def download_unsplash_image():
    """Lädt ein zufälliges Bild von Unsplash herunter."""
    if not UNSPLASH_ACCESS_KEY:
        raise ValueError(
            "UNSPLASH_ACCESS_KEY nicht gesetzt. "
            "Bitte Umgebungsvariable setzen oder .env Datei erstellen."
        )
    
    # API-Parameter
    params = {
        'query': QUERY,
        'orientation': ORIENTATION,
        'client_id': UNSPLASH_ACCESS_KEY
    }
    
    print("Lade Bild von Unsplash...")
    response = requests.get(UNSPLASH_API_URL, params=params)
    
    if response.status_code != 200:
        raise Exception(
            f"Fehler beim Abrufen des Bildes: {response.status_code} - {response.text}"
        )
    
    data = response.json()
    
    # Download-URL für volle Auflösung
    image_url = data['urls']['full']
    photographer = data['user']['name']
    photo_id = data['id']
    
    print(f"Bild von {photographer} (ID: {photo_id})")
    
    # Bild herunterladen
    image_response = requests.get(image_url, stream=True)
    
    if image_response.status_code != 200:
        raise Exception(f"Fehler beim Herunterladen des Bildes: {image_response.status_code}")
    
    # Bild speichern
    with open(CURRENT_WALLPAPER, 'wb') as f:
        for chunk in image_response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"Bild gespeichert: {CURRENT_WALLPAPER}")
    
    # Metadaten speichern
    metadata_file = WALLPAPER_DIR / 'metadata.txt'
    with open(metadata_file, 'w') as f:
        f.write(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Fotograf: {photographer}\n")
        f.write(f"Unsplash ID: {photo_id}\n")
        f.write(f"URL: https://unsplash.com/photos/{photo_id}\n")
    
    return CURRENT_WALLPAPER


def set_wallpaper_gnome(image_path):
    """Setzt das Hintergrundbild für GNOME/Ubuntu."""
    subprocess.run([
        'gsettings', 'set', 'org.gnome.desktop.background', 
        'picture-uri', f'file://{image_path}'
    ])
    subprocess.run([
        'gsettings', 'set', 'org.gnome.desktop.background', 
        'picture-uri-dark', f'file://{image_path}'
    ])
    print("Hintergrundbild für GNOME gesetzt.")


def set_wallpaper_kde(image_path):
    """Setzt das Hintergrundbild für KDE Plasma."""
    script = f"""
    var allDesktops = desktops();
    for (i = 0; i < allDesktops.length; i++) {{
        d = allDesktops[i];
        d.wallpaperPlugin = "org.kde.image";
        d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
        d.writeConfig("Image", "file://{image_path}");
    }}
    """
    subprocess.run(['qdbus', 'org.kde.plasmashell', '/PlasmaShell', 
                   'org.kde.PlasmaShell.evaluateScript', script])
    print("Hintergrundbild für KDE Plasma gesetzt.")


def set_wallpaper_xfce(image_path):
    """Setzt das Hintergrundbild für XFCE."""
    subprocess.run([
        'xfconf-query', '--channel', 'xfce4-desktop',
        '--property', '/backdrop/screen0/monitor0/workspace0/last-image',
        '--set', str(image_path)
    ])
    print("Hintergrundbild für XFCE gesetzt.")


def set_wallpaper_feh(image_path):
    """Setzt das Hintergrundbild mit feh (für i3, bspwm, etc.)."""
    subprocess.run(['feh', '--bg-scale', str(image_path)])
    print("Hintergrundbild mit feh gesetzt.")


def detect_and_set_wallpaper(image_path):
    """Erkennt die Desktop-Umgebung und setzt das Hintergrundbild entsprechend."""
    desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    
    try:
        if 'gnome' in desktop_env or 'ubuntu' in desktop_env:
            set_wallpaper_gnome(image_path)
        elif 'kde' in desktop_env or 'plasma' in desktop_env:
            set_wallpaper_kde(image_path)
        elif 'xfce' in desktop_env:
            set_wallpaper_xfce(image_path)
        else:
            # Fallback zu feh
            print(f"Desktop-Umgebung '{desktop_env}' nicht erkannt, versuche feh...")
            set_wallpaper_feh(image_path)
    except FileNotFoundError as e:
        print(f"Fehler: Benötigtes Tool nicht gefunden. {e}")
        print("Bitte installiere die entsprechenden Tools für deine Desktop-Umgebung.")
    except Exception as e:
        print(f"Fehler beim Setzen des Hintergrundbilds: {e}")


def main():
    """Hauptfunktion."""
    try:
        print("=== Unsplash Daily Wallpaper Changer ===")
        setup_directories()
        image_path = download_unsplash_image()
        detect_and_set_wallpaper(image_path)
        print("Fertig!")
    except Exception as e:
        print(f"Fehler: {e}")
        exit(1)


if __name__ == '__main__':
    main()
