#!/bin/bash
# Setup Script für COSMIC Greeter Login-Hintergrund
# Muss einmalig mit sudo ausgeführt werden

set -e

WALLPAPER_SOURCE="$HOME/.local/share/wallpapers/current_wallpaper.jpg"
COSMIC_BG_DIR="/usr/share/backgrounds/cosmic"
COSMIC_BG_FILE="$COSMIC_BG_DIR/login-wallpaper.jpg"

echo "=== COSMIC Greeter Login-Hintergrund Setup ==="

# Erstelle Verzeichnis falls nicht vorhanden
if [ ! -d "$COSMIC_BG_DIR" ]; then
    echo "Erstelle Verzeichnis: $COSMIC_BG_DIR"
    sudo mkdir -p "$COSMIC_BG_DIR"
fi

# Kopiere aktuelles Wallpaper
if [ -f "$WALLPAPER_SOURCE" ]; then
    echo "Kopiere Wallpaper nach $COSMIC_BG_FILE"
    sudo cp "$WALLPAPER_SOURCE" "$COSMIC_BG_FILE"
    sudo chmod 644 "$COSMIC_BG_FILE"
    echo "✓ Login-Hintergrund wurde gesetzt!"
    echo ""
    echo "Das Bild wird beim nächsten Logout/Login angezeigt."
else
    echo "Fehler: Wallpaper nicht gefunden: $WALLPAPER_SOURCE"
    echo "Bitte führe zuerst 'python3 change_wallpaper.py' aus."
    exit 1
fi

echo ""
echo "Hinweis: Führe dieses Script nach jedem Wallpaper-Wechsel aus,"
echo "um auch den Login-Hintergrund zu aktualisieren:"
echo "  ./setup-login-wallpaper.sh"
