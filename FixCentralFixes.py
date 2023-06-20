from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
import pandas as pd
from datetime import date
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Alignment, Font

def main():
    # Open broswer using headless argument to avoid having a firefox window visually opened
    options = Options()
    options.add_argument("-headless")
    browser = webdriver.Firefox(options = options)
    
    # Get user input for the link of search query that is needed to scrape as well as how many results they would like to retain
    url = input("After searching for the fixes, please paste the url into terminal and hit enter:\n")
    numberOfEntries = input("How many results would you like to retrieve? (10/20/40/All) [If choosing all please enter -1]:\n")

    # Insert the link of search query we would like to scrape
    browser.get(url)

    # Initialize list that will keep all necessary info of fixes
    fixes = []

    # Wait for elements to load on page prior to proceeding
    try:
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, 'fcselectFixesresults_length')))
    except:
        print("Show results took too long to load")

    # Set results to show all (Needed because HTML only loads the information for the fixes that are shown)
    # Values available are 10, 20, 40, -1 (All)
    showDD = Select(browser.find_element(By.NAME, 'fcselectFixesresults_length'))
    showDD.select_by_value(numberOfEntries)

    # Show Fix details to access all details needed 
    # Removing for now as these details are loaded through HTML without having to click the button, may have to reimplement in the future
    # browser.find_element(By.CLASS_NAME, 'fc-show-results').click()
 

    # Get name for excel doc
    tempTitle = browser.find_element(By.ID, 'fc-subtitle')
    title = tempTitle.text

    # Store all available fixes and fix details
    chunks = browser.find_elements(By.CLASS_NAME, 'fc-all')

    for chunk in chunks:
        # Get Fix ID in text form 
        fixID = chunk.find_element(By.XPATH, './/p/a').text

        # Get description of the fix, remove unnecessary text and whitespace
        tempDescription = chunk.find_element(By.XPATH, './/div[1]/p[6]').get_attribute('textContent')
        description = tempDescription.split("Abstract:",1)[1]
        description = description.strip()

        # Initialize lists to hold scores and cves when getAparCveScore gets called
        scores = []
        cves = []

        # Get fix link provided, and return none provided if none is found
        try:
            tempAparLink = chunk.find_element(By.CLASS_NAME, 'ibm-popup-link')
            aparLink = tempAparLink.get_attribute('href') 
        except:
            aparLink = 'None provided'
        
        try:
            apar, scores, cves = getAparCveScore(aparLink)
        except:
            apar = 'Not Found'
        
        # Create a dictionary item that contains all fix information
        fix_item = {
            'APAR' : apar,
            'Description' : description,
            'CVE ID': cves,
            'CVSS Base Score': scores,
            'Fix ID': fixID,
            'Bulletin Link': aparLink
        }

        # Providing visual feedback through terminal of objects being created
        print(fix_item)

        # Append fix list with current fix details
        fixes.append(fix_item)

    # Create dataframe with all details gathered
    df = pd.DataFrame(fixes, columns = ['APAR', 'Description', 'CVE ID', 'CVSS Base Score', 'Fix ID', 'Bulletin Link'])
    df.to_excel(title + ' Fixes.xlsx')

    # Closes main browser to ensure no more memory being used
    browser.quit()
    print("All fixes gathered, check the created document for all details" )

# Function to retrieve the APAR number, CVE IDs, and CVSS Base scores associated with the fix
def getAparCveScore(link):

    # Boolean that lets program know when the details have been found to not do any other try/except clause if not needed
    notFound = 1

    # Start new webdriver for the page containing details
    options = Options()
    options.add_argument ("-headless")
    browser = webdriver.Firefox(options=options)
    browser.get(link)

    # Initialize variables to hold all data, CVSS Base scores, and CVE IDs respectively
    scores = []
    cves = []
    apar = ''

    # Deals with cookies popup
    try:
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'truste-consent-track')))
        browser.execute_script("document.getElementById('truste-consent-track').style.display = 'none';")
    except:
        pass
    
    if(notFound):
        # Gets APAR document number if available
        try:
            (WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'caption-01'))))
            apar = browser.find_element(By.XPATH, '//c-r2-carbon-accordion-item/li/div/slot/div/div/div[3]/p[2]').text
        except:
            #apar = 'Not Loaded'
            pass

        # Clicks Show More button if necessary, otherwise cannot gather all data
        try:
            WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".showMore")))
            browser.find_element(By.CSS_SELECTOR, ".showMore").click()
        except:
            pass

        # Finds all element that contain data needed
        chunks = browser.find_elements(By.XPATH, '//c-r2-known-issues-display-tile[1]/c-r2-carbon-accordion/ul/slot/c-r2-carbon-accordion-item/li/div/slot/p/lightning-formatted-rich-text/span/p')
        
        # Traverse through all data and capture any relevant data
        for chunk in chunks:
            line = chunk.text    
            if ("CVSS Base Score:" in line):
                line = line.removeprefix('CVSS Base Score:')
                line = line.removeprefix('CVSS Base score:')
                line = line.strip()
                scores.append(line)
            elif("CVSS Base score:" in line):
                line = line.removeprefix('CVSS Base Score:')
                line = line.removeprefix('CVSS Base score:')
                line = line.strip()
                scores.append(line)
            elif ("CVEID" in line):
                line = line.removeprefix('CVEID:')
                line = line.strip()
                cves.append(line)
        

    if not scores and not cves:
        # If page has details loaded in /pre HTML tag
        try:

            # Try to retrieve APAR number
            try:
                (WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ibm-stock-list'))))
                apar = browser.find_element(By.XPATH, "//div[3]/div/div/ul/li[1]/p").text
            except:
                apar = 'Not Loaded'

            # Find all elements with /pre tag and store them in tempChunks
            # Separate each block of /pre into chunks and convert into text while also splittinat at every new line
            # Try except just to pass in case anything goes wrong so browser closes properly
            try:
                tempChunks = browser.find_elements(By.XPATH, "//pre")
                chunks = []
                for i in tempChunks:
                    chunks.append(i.text.splitlines())
            except:
                pass
            
            # Retrieve the text block that has all the information necessary and split by delimiter ',' 
            mainText = str(chunks[0])
            mainText = mainText.split(',')

            # Strip unnecessary text and append respective lists
            for line in mainText:
                if ("CVSS Base" in line):
                    line = line.replace("'CVSS Base Score:", '')
                    line = line.replace("'CVSS Base score:", '')
                    line = line.replace("'", '')
                    line = line.strip()
                    scores.append(line)
                    
                elif ("CVEID" in line):
                    line = line.replace('CVEID:', '')
                    line = line.replace("'", '')
                    line = line.replace("[", '')
                    line = line.strip()
                    cves.append(line)
        except:
            pass
    # Closes browser instance to avoid unnecessary memory being used
    browser.quit()

    return apar, scores, cves


if __name__ == "__main__":
    main()