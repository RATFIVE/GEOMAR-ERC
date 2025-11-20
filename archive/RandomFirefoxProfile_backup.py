import random

# Driver for Firefox, Chrome, Edge, etc.
from selenium import webdriver
import tempfile





class RandomFirefoxProfile:
    """Erstellt zufällige Firefox-Profile."""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    LANGUAGES = ["en-US", "en-GB", "de-DE", "fr-FR", "es-ES"]
    
    SCREEN_RESOLUTIONS = [
        (1920, 1080),
        (1366, 768),
        (1440, 900),
        (1536, 864),
        (1280, 720),
    ]
    
    @staticmethod
    def create():
        """Erstellt ein zufälliges Firefox-Profil."""
        
        # Temporäres Profil
        temp_dir = tempfile.mkdtemp(prefix="firefox_")
        profile = webdriver.FirefoxProfile(temp_dir)
        
        # Zufälliger User-Agent
        user_agent = random.choice(RandomFirefoxProfile.USER_AGENTS)
        profile.set_preference("general.useragent.override", user_agent)
        
        # Zufällige Sprache
        language = random.choice(RandomFirefoxProfile.LANGUAGES)
        profile.set_preference("intl.accept_languages", language)
        
        # Download-Einstellungen
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.dir", "/tmp")
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
        
        # Anti-Detection
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference("useAutomationExtension", False)
        profile.set_preference("privacy.trackingprotection.enabled", True)
        
        # Zufällige Viewport-Größe (simuliert verschiedene Bildschirme)
        width, height = random.choice(RandomFirefoxProfile.SCREEN_RESOLUTIONS)
        profile.set_preference("layout.css.devPixelsPerPx", str(random.uniform(0.9, 1.1)))
        
        # WebGL und Canvas Fingerprinting reduzieren
        profile.set_preference("webgl.disabled", random.choice([True, False]))
        profile.set_preference("privacy.resistFingerprinting", True)
        
        print("🎲 Zufälliges Profil erstellt:")
        print(f"   User-Agent: {user_agent[:50]}...")
        print(f"   Sprache: {language}")
        print(f"   Auflösung: {width}x{height}")
        
        return profile