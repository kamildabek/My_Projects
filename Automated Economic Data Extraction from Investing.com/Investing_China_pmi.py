import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import time

def scrape_investing_data(url, event_id, show_more_button_id, table_id, stop_year, output_csv):
    # Automatyczna instalacja najnowszej wersji ChromeDriver
    chromedriver_autoinstaller.install()

    # Ustawienia opcji przeglądarki
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Możesz usunąć, jeśli chcesz widzieć okno przeglądarki
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Tworzenie obiektu ChromeDriver wewnątrz funkcji
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Otwórz stronę Investing.com
        driver.get(url)

        # Poczekaj, aż dane się załadują
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, show_more_button_id)))

        # Pobierz wiersze tabeli
        rows = driver.find_elements(By.XPATH, f"//table[@id='{table_id}']/tbody/tr")

        # Kliknij "Załaduj więcej" i pobierz dodatkowe dane
        try:
            while True:
                driver.execute_script(f"ecEvent.moreHistory({event_id}, document.getElementById('{show_more_button_id}'), 0)")
                time.sleep(3)  # Czekaj na załadowanie nowych danych
                new_rows = driver.find_elements(By.XPATH, f"//table[@id='{table_id}']/tbody/tr")
                if len(new_rows) == len(rows):
                    break  # Jeśli dane się nie zmieniły, zakończ pętlę
                rows = new_rows
        except Exception as e:
            print("Wystąpił błąd lub wszystkie dane zostały załadowane:", e)

        # Pobranie nagłówków tabeli
        headers = [header.text for header in driver.find_elements(By.XPATH, f"//table[@id='{table_id}']/thead/tr/th")]

        # Pobranie danych z tabeli
        data = []
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            row_data = [column.text for column in columns]
            data.append(row_data)

            # Jeśli rok jest mniejszy niż stop_year, przerwij
            if any(str(stop_year) in cell for cell in row_data):
                break

        # Tworzenie DataFrame i zapis do CSV
        df = pd.DataFrame(data, columns=headers)
        df.to_csv(output_csv, index=False)
        print(f"Zebrano dane do roku {stop_year} i zapisano do pliku {output_csv}.")

    except Exception as e:
        print("Błąd w trakcie pobierania danych:", e)

    finally:
        driver.quit()  # Zamykanie przeglądarki nawet w przypadku błędu

# Automatyczne pobranie ścieżki do Dokumentów użytkownika
documents_path = os.path.join(os.getenv("USERPROFILE"), "Documents")
os.makedirs(documents_path, exist_ok=True)  # Tworzenie katalogu, jeśli nie istnieje
output_csv = os.path.join(documents_path, "China_manufacturing_pmi_2010_and_later.csv")

# PRZYKŁAD UŻYCIA:
url = "https://www.investing.com/economic-calendar/chinese-manufacturing-pmi-594"
event_id = 594
show_more_button_id = "showMoreHistory594"
table_id = "eventHistoryTable594"
stop_year = 2010

scrape_investing_data(url, event_id, show_more_button_id, table_id, stop_year, output_csv)
