import pytest
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import platform

# Configuration
SELENIUM_GRID_URL = "http://localhost:4444"
WAIT_TIMEOUT = 30  # secondes

# Déterminer l'URL de l'application en fonction du système
if platform.system() == "Windows":
    APP_URL = "http://host.docker.internal:5000"
else:
    # Pour Linux/Mac, utilisez l'IP du réseau Docker
    APP_URL = "http://172.17.0.1:5000"

def check_app_availability():
    """Vérifie si l'application Flask est accessible"""
    try:
        # Vérifier localement
        response = requests.get("http://127.0.0.1:5000")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

@pytest.fixture(params=["chrome", "firefox"])
def browser(request):
    """Fixture pour initialiser le navigateur avec Selenium Grid"""
    # Vérifier si l'application est disponible
    if not check_app_availability():
        pytest.skip("L'application Flask n'est pas accessible")

    driver = None
    for attempt in range(3):
        try:
            if request.param == "chrome":
                chrome_options = ChromeOptions()
                chrome_options.set_capability("browserName", "chrome")
                # Ajouter des options pour la stabilité
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--dns-prefetch-disable")
                driver = webdriver.Remote(
                    command_executor=SELENIUM_GRID_URL,
                    options=chrome_options
                )
                break
            elif request.param == "firefox":
                firefox_options = FirefoxOptions()
                firefox_options.set_capability("browserName", "firefox")
                # Ajouter des options pour la stabilité
                firefox_options.set_capability("acceptInsecureCerts", True)
                driver = webdriver.Remote(
                    command_executor=SELENIUM_GRID_URL,
                    options=firefox_options
                )
                break
        except Exception as e:
            print(f"Tentative {attempt + 1} échouée: {str(e)}")
            if attempt == 2:
                raise
            time.sleep(5)

    if driver is None:
        pytest.fail("Impossible de se connecter à Selenium Grid")

    driver.set_page_load_timeout(WAIT_TIMEOUT)
    driver.implicitly_wait(10)
    
    # Maximiser la fenêtre pour éviter les problèmes d'éléments non visibles
    driver.maximize_window()
    
    yield driver
    
    try:
        driver.quit()
    except Exception as e:
        print(f"Erreur lors de la fermeture du navigateur: {str(e)}")

def test_registration_and_login(browser):
    """Test le processus d'inscription et de connexion"""
    try:
        print(f"Tentative d'accès à {APP_URL}/register")
        
        # 1. Accéder à la page d'inscription
        browser.get(f"{APP_URL}/register")
        WebDriverWait(browser, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        # 2. Remplir le formulaire d'inscription
        username = f"testuser_{int(time.time())}"
        browser.find_element(By.NAME, "username").send_keys(username)
        browser.find_element(By.NAME, "email").send_keys(f"{username}@example.com")
        browser.find_element(By.NAME, "password").send_keys("passer")
        browser.find_element(By.NAME, "adresse").send_keys("golf")
        
        # Attendre que le bouton soit cliquable
        submit_button = WebDriverWait(browser, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.NAME, "envoie"))
        )
        submit_button.click()

        # 3. Vérifier la redirection vers la page de connexion
        WebDriverWait(browser, WAIT_TIMEOUT).until(
            EC.title_contains("Login")
        )
        assert "Login" in browser.title

        # 4. Se connecter
        browser.get(f"{APP_URL}/login")
        WebDriverWait(browser, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        browser.find_element(By.NAME, "username").send_keys(username)
        browser.find_element(By.NAME, "password").send_keys("passer")
        
        # Attendre que le bouton soit cliquable
        login_button = WebDriverWait(browser, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.NAME, "envoies"))
        )
        login_button.click()

        # 5. Vérifier la redirection vers la page d'accueil
        WebDriverWait(browser, WAIT_TIMEOUT).until(
            EC.title_contains("Accueil")
        )
        assert "Accueil" in browser.title

    except Exception as e:
        print(f"Erreur pendant le test: {str(e)}")
        # Prendre une capture d'écran en cas d'erreur
        browser.save_screenshot(f"error_{int(time.time())}.png")
        raise e

if __name__ == "__main__":
    pytest.main(["-v"])