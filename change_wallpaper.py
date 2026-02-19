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

# .env Datei laden falls vorhanden
def load_env():
    """Lädt Umgebungsvariablen aus .env Datei."""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                # Überspringe Kommentare und leere Zeilen
                if line and not line.startswith('#'):
                    key, _, value = line.partition('=')
                    os.environ[key.strip()] = value.strip()

load_env()

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
            "Bitte .env Datei erstellen (siehe .env.example)."
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


def set_wallpaper_cosmic(image_path):
    """Setzt das Hintergrundbild für COSMIC Desktop."""
    # COSMIC speichert Wallpaper-Konfiguration in RON-Dateien
    cosmic_config_dir = Path.home() / '.config' / 'cosmic' / 'com.system76.CosmicBackground' / 'v1'
    
    if cosmic_config_dir.exists():
        # RON-Format für COSMIC Background
        ron_content = f"""(
    output: "all",
    source: Path("{image_path}"),
    filter_by_theme: true,
    rotation_frequency: 300,
    filter_method: Lanczos,
    scaling_mode: Zoom,
    sampling_method: Alphanumeric,
)"""
        
        # Schreibe die Konfiguration
        all_config = cosmic_config_dir / 'all'
        with open(all_config, 'w') as f:
            f.write(ron_content)
        
        # Optional: same-on-all Datei aktualisieren falls vorhanden
        same_on_all = cosmic_config_dir / 'same-on-all'
        if same_on_all.exists():
            with open(same_on_all, 'w') as f:
                f.write("true")
        
        print("Hintergrundbild für COSMIC gesetzt (RON-Konfiguration).")
        
        # Versuche COSMIC Background neu zu laden
        try:
            # cosmic-bg könnte helfen die Änderungen zu übernehmen
            subprocess.run(['cosmic-bg'], timeout=2, capture_output=True)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return
    
    # Fallback: Versuche GNOME gsettings (funktioniert bei manchen COSMIC-Versionen)
    try:
        subprocess.run([
            'gsettings', 'set', 'org.gnome.desktop.background', 
            'picture-uri', f'file://{image_path}'
        ], check=True, timeout=5)
        subprocess.run([
            'gsettings', 'set', 'org.gnome.desktop.background', 
            'picture-uri-dark', f'file://{image_path}'
        ], timeout=5)
        print("Hintergrundbild für COSMIC gesetzt (gsettings).")
        return
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    
    # Wenn nichts funktioniert, werfe einen Fehler
    raise FileNotFoundError("Konnte kein unterstütztes Tool für COSMIC finden")


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


def set_login_wallpaper_cosmic(image_path):
    """Setzt das Hintergrundbild für den COSMIC Greeter (Login-Bildschirm)."""
    try:
        # Verwende cosmic-greeter-config CLI tool (falls verfügbar)
        result = subprocess.run(
            ['cosmic-greeter-config', 'background', str(image_path)],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("Login-Hintergrundbild für COSMIC Greeter gesetzt.")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Alternative: Verwende dbus um mit cosmic-greeter-daemon zu kommunizieren
    try:
        # Kopiere das Bild in ein systemweites Verzeichnis
        system_wallpaper_dir = Path('/usr/share/backgrounds/cosmic')
        if not system_wallpaper_dir.exists():
            # Erstelle Anleitung für manuelles Setup
            print("\nUm den Login-Hintergrund für COSMIC Greeter zu setzen:")
            print(f"1. Kopiere das Bild in ein systemweites Verzeichnis:")
            print(f"   sudo mkdir -p /usr/share/backgrounds/cosmic")
            print(f"   sudo cp {image_path} /usr/share/backgrounds/cosmic/login-wallpaper.jpg")
            print(f"2. Der COSMIC Greeter sollte das Bild dann automatisch verwenden.")
            return False
        
        # Wenn das Verzeichnis existiert, versuche das Bild zu kopieren
        system_wallpaper = system_wallpaper_dir / 'login-wallpaper.jpg'
        result = subprocess.run(
            ['sudo', 'cp', str(image_path), str(system_wallpaper)],
            timeout=10
        )
        if result.returncode == 0:
            print("Login-Hintergrundbild für COSMIC Greeter gesetzt.")
            return True
    except Exception as e:
        print(f"Konnte Login-Hintergrund nicht automatisch setzen: {e}")
    
    return False


def set_login_wallpaper_gdm(image_path):
    """Setzt das Hintergrundbild für GDM (GNOME Display Manager)."""
    # GDM verwendet AccountsService
    # Dies erfordert root-Rechte, daher erstellen wir nur eine Datei die ein Admin später installieren kann
    user = os.environ.get('USER', os.environ.get('LOGNAME', ''))
    
    # AccountsService Hintergrund
    accountsservice_bg = Path(f'/var/lib/AccountsService/users/{user}')
    
    # Überprüfe ob AccountsService existiert
    if not Path('/var/lib/AccountsService').exists():
        return False
    
    # Erstelle eine temporäre Konfiguration die mit sudo kopiert werden kann
    temp_config = WALLPAPER_DIR / 'gdm-background-config.txt'
    with open(temp_config, 'w') as f:
        f.write(f"[User]\n")
        f.write(f"Background={image_path}\n")
    
    print(f"GDM Konfiguration erstellt: {temp_config}")
    print(f"Um den Login-Hintergrund für GDM zu setzen, führe aus:")
    print(f"  sudo cp {temp_config} {accountsservice_bg}")
    print(f"  sudo chmod 644 {accountsservice_bg}")
    
    return True


def detect_and_set_wallpaper(image_path):
    """Erkennt die Desktop-Umgebung und setzt das Hintergrundbild entsprechend."""
    desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    
    try:
        if 'cosmic' in desktop_env:
            set_wallpaper_cosmic(image_path)
        elif 'gnome' in desktop_env or 'ubuntu' in desktop_env:
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
        print(f"\nFür COSMIC: Das Bild wurde heruntergeladen nach: {image_path}")
        print("Du kannst es manuell in den COSMIC Einstellungen setzen.")
    except Exception as e:
        print(f"Fehler beim Setzen des Hintergrundbilds: {e}")


def detect_and_set_login_wallpaper(image_path):
    """Erkennt den Login-Manager und setzt das Login-Hintergrundbild."""
    desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    
    print("\n--- Login-Hintergrund setzen ---")
    
    success = False
    
    # Versuche COSMIC Greeter
    if 'cosmic' in desktop_env:
        success = set_login_wallpaper_cosmic(image_path)
        if success:
            return
    
    # Versuche GDM (wird auch von COSMIC manchmal verwendet)
    if set_login_wallpaper_gdm(image_path):
        success = True
    
    if not success:
        print("Login-Hintergrund konnte nicht automatisch gesetzt werden.")
        print(f"Das Bild ist verfügbar unter: {image_path}")


def main():
    """Hauptfunktion."""
    try:
        print("=== Unsplash Daily Wallpaper Changer ===")
        setup_directories()
        image_path = download_unsplash_image()
        detect_and_set_wallpaper(image_path)
        detect_and_set_login_wallpaper(image_path)
        print("\nFertig!")
    except Exception as e:
        print(f"Fehler: {e}")
        exit(1)


if __name__ == '__main__':
    main()
