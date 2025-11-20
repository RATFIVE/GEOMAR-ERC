from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from random import uniform
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# eigene Module
from RandomFirefoxProfile import RandomFirefoxProfile

class ResearchGateSelenium:

    def __init__(self, name: str = "Gregor-Anderluh", headless: bool = True):
        self.BASE_URL = 'https://www.researchgate.net/'
        self.name = name.replace(" ", "-")
        self.headless = headless
        self.driver = None
    
    def get_driver(self):
        """Initialisiert den Firefox WebDriver."""
        if self.driver is not None:
            return self.driver
        
        options = webdriver.FirefoxOptions()
        if self.headless:
            options.add_argument("--headless")

        # Docker-spezifische Optionen
        options.add_argument("--no-sandbox") # Notwendig in Docker-Umgebungen
        options.add_argument("--disable-dev-shm-usage") # Verhindert Probleme mit gemeinsam genutztem Speicher

        profile = RandomFirefoxProfile.create()
        options.profile = profile

        try:
            service = Service(executable_path="/usr/local/bin/geckodriver")
            self.driver = webdriver.Firefox(options=options, service=service)
        except Exception as e:
            print(f"⚠️ Fehler beim Starten des WebDrivers: {e}")
        
        try:
            self.driver = webdriver.Firefox(options=options)
        except Exception as e:
                print(f"⚠️ Fehler beim Starten des WebDrivers: {e}")

        return self.driver
    
    def close_driver(self):
        """Beendet den WebDriver sicher."""
        if self.driver is not None:
            try:
                self.driver.quit()
                self.driver = None
            except Exception as e:
                print(f"⚠️ Fehler beim Schließen: {e}")
            finally:
                self.driver = None
    
    def random_sleep(self, min_seconds=1.0, max_seconds=3.0):
        """Zufällige Wartezeit."""
        sleep_time = uniform(min_seconds, max_seconds)
        sleep(sleep_time)
        return sleep_time
    
    def access_denied_check(self):
        """Prüft auf Access Denied."""
        try:
            page_html = self.driver.page_source if self.driver else ""
            if "<h1>Access denied</h1>" in page_html:
                print("⚠️ Access denied detected.")
                return True
            return False
        except Exception as e:
            print(f"⚠️ Fehler bei Access Check: {e}")
            return False
    
    def klick_privacy_accept(self):
        """Klickt auf Privacy-Accept-Button."""
        try:
            self.random_sleep(1, 2)
            wait = WebDriverWait(self.driver, 10) if self.driver else None
            agree_button = wait.until(
                EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
            ) if wait else None
            agree_button.click() if agree_button else None
            print("✅ Privacy-Banner akzeptiert")
        except Exception as e:
            print(f"ℹ️ Kein Privacy-Banner gefunden (bereits akzeptiert?)")
    
    def find_skills(self):
        """Extrahiert Skills vom ResearchGate-Profil."""
        
        # 1. Driver initialisieren
        self.get_driver()
        
        # 2. Zur Profilseite navigieren
        profile_url = f"{self.BASE_URL}profile/{self.name}"
        print(f"🌐 Öffne: {profile_url}")
        
        try:
            self.driver.get(profile_url) if self.driver else None
            self.driver.implicitly_wait(10) if self.driver else None
            
            # 3. Privacy-Banner akzeptieren
            self.klick_privacy_accept()
            self.random_sleep(2, 4)
            #self.driver.refresh()
            
            # 4. Access Denied prüfen
            if self.access_denied_check():
                
                self.close_driver()
                sleep_time = uniform(15, 20)
                print(f"⚠️ Zugriff verweigert. Warte {round(sleep_time, 1)} Sekunden...")
                sleep(sleep_time)
                return self.find_skills()  # Rekursiver Aufruf
            
            # 5. Skills-Element finden (mehrere Selektoren probieren)
            introduction = None
            
            selectors = [
                (By.CSS_SELECTOR, "div.nova-legacy-c-card:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1)"),
                (By.XPATH, "/html/body/div[2]/main/section[3]/div/div[2]/div[2]/div/div"),
                (By.CSS_SELECTOR, "div.nova-legacy-c-card--spacing-xl div.nova-legacy-o-stack__item"),
            ]
            
            for by, selector in selectors:
                try:
                    introduction = self.driver.find_element(by, selector) if self.driver else None
                    print(f"✅ Element gefunden mit: {by} - {selector[:50]}...")
                    break
                except Exception:
                    continue
            
            if not introduction:
                print("❌ Skills-Bereich nicht gefunden")
                return None
            
            # 6. Text extrahieren
            introduction_text = introduction.text
            
            # 7. In Liste konvertieren
            skills_list = [
                skill.strip() 
                for skill in introduction_text.split('\n') 
                if skill.strip() and skill.strip() != 'Skills and Expertise'
            ]
            
            print(f"✅ {len(skills_list)} Skills gefunden")
            return skills_list
        
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Skills: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        finally:
            # 8. Driver schließen (immer!)
            self.close_driver()