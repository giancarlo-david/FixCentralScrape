# FixCentralScrape

## Description
A web scraper that retrieves data from IBM's Fix Central page for fixes with the product of your choice
---
## Objective
Create an automated way to gather details (APAR, Description, CVEIDs, CVSS Base scores, Fix IDs, Bulletin Links) about each fix for a given product and its respective version and output to an xls format
---
## How It Works
The user has to search the product and version they want to search fixes for and once the search query is finished, the user takes the url and uses it within the program along with how many search reasults they would like to obtain information of.

The program then goes through the entire table and scrapes the necessary data (Description, FixID, Bulletin Link) from the table.

Afterwards, the program will go through each security bulletin link that would then gather the rest of the information necessary.
---
## To Do List
-  [ ] Find out why Fix IDs do not get retrieved after a certain point and fix
-  [ ] Find out why some APAR numbers are still not being retrieved (pretty sure APAR gets changed, easy way to fix is getting the end of the Fix ID for the APAR but have to fix first issue first)
-  [ ] Look for ways to optimize (Multithreading is an option)
---
## Learnings
This project has taught me a multitude of lessons that I can use in future projects such as 
- Foundational knowledge of the Selenium package
- HTML structure and syntax (mainly how tags, classes, ids, and names)
- In depth knowledge on how XPath and searching for XPath works
- Intricaciess of making a web scraper work properly
