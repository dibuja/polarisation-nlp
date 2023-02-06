'''
This script uses Selenium to go to https://congreso.es and obtain all the interventions for a given period of time.
There was no need to change the User Agent of the webdriver or use other anti-blocking techniques since the website
allows scrapping. The sleep() methods are there to prevent the server from blocking the connection to the IP.
'''

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from datetime import date, timedelta
from time import sleep

# We obtain the total amount of days to iterate over.
d1 = date(2023, 1, 24)
d2 = date(2023, 2, 5)
delta = (d2 - d1).days

period = 7 # Amount of days to iterate over.

# Initialize the web driver and open the website.
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://www.congreso.es/busqueda-de-intervenciones?p_p_id=intervenciones&_intervenciones_statusOpenData=true")

for i in range(0, delta, period):
    num = []
    since = 0
    until = 0

    since = d1 + timedelta(i)
    until = since + timedelta(period)

    since = str(f'{since:%d/%m/%Y}')
    until = str(f'{until:%d/%m/%Y}')

    script_since = f"document.getElementById('_intervenciones_fecDesde').value = '{since}'"
    script_until = f"document.getElementById('_intervenciones_fecHasta').value = '{until}'"

    driver.execute_script("document.getElementById('_intervenciones_legislatura').selectedIndex = '0'")

    driver.execute_script(script_since)

    sleep(0.5)

    driver.execute_script(script_until)

    driver.execute_script("resetSavedSearchIntervenciones()")

    driver.execute_script("crearListado(1, 1)")

    # Get the total number of results
    # The structure of the text changes 
    # depending on the size of the output

    sleep(4)

    while len(num) == 0:
        num = driver.find_element('id', '_intervenciones_resultsShowedIntervenciones')
        num = num.text.split()

    if len(num) < 3:
        num = int(num[0])
    else:
        num = int(num[len(num) - 1])

    if num > 1000:
        print(f'<1000 results. On dates since: {since}; until: {until}')

    # Only download when there is something to download.
    if num != 0:

        # Export the results to CSV.
        driver.execute_script("exportOpendata('csv')")

        sleep(0.5)

        for current in range(1, num, 100):
            # Script with argument for downloading the specific page

            download_script = f"downloadFile({current}, {num}, 'csv')"

            # Run the script
            driver.execute_script(download_script)

            sleep(0.5)
