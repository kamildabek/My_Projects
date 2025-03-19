import requests
import xmltodict
import pandas as pd
import time

# Lista regionów dostępnych w API World Bank
regions = ["AFE", "EAS", "ECS", "LCN", "MEA", "NAC", "SAS", "SSF"]

# Pusty słownik na dane (będzie zawierał DataFrame dla każdego regionu)
region_dataframes = {}

# Pobieranie danych dla każdego regionu
for region in regions:
    print(f" Fetching data for region: {region}...")

    # URL API Banku Światowego (dla populacji)
    api_url = f"http://api.worldbank.org/v2/country/{region}/indicator/SP.POP.TOTL?format=xml"

    # Wysyłanie żądania do API
    response = requests.get(api_url)

    # Debugowanie odpowiedzi
    print(f"Response status code: {response.status_code}")

    # Obsługa błędów HTTP
    if response.status_code != 200:
        print(f"❌ API error for {region}: {response.status_code}")
        continue

    # Usuwanie niepotrzebnych znaków BOM i dekodowanie
    xml_data = response.content.decode("utf-8-sig")

    # Parsowanie XML
    try:
        data_dict = xmltodict.parse(xml_data)

        if "wb:data" in data_dict:
            population_data = data_dict["wb:data"].get("wb:data", [])

            # Tworzenie DataFrame dla regionu
            df = pd.DataFrame([
                {
                    "Indicator": entry.get("wb:indicator", {}).get("#text", "Unknown"),
                    "Country": entry.get("wb:country", {}).get("#text", "Unknown"),
                    "ISO3": entry.get("wb:countryiso3code", "Unknown"),
                    "Year": entry.get("wb:date", "Unknown"),
                    "Population": entry.get("wb:value", "0")
                }
                for entry in population_data
            ])

            # Dodanie DataFrame do słownika
            region_dataframes[region] = df
            print(f"✅ Data for {region} processed successfully.")

    except Exception as e:
        print(f"❌ XML parsing error for {region}: {e}")
        continue

    # Opóźnienie, aby uniknąć blokady API
    time.sleep(1)

# 🔹 Zapis do pliku Excel (każdy region w osobnym arkuszu)
if region_dataframes:
    output_excel = "WorldBank_Population_All_Regions.xlsx"

    with pd.ExcelWriter(output_excel, engine="xlsxwriter") as writer:
        for region, df in region_dataframes.items():
            df.to_excel(writer, sheet_name=region, index=False)

    print(f"✅ All regions saved to Excel file: {output_excel}")
else:
    print("❌ No data was collected. No Excel file created.")
