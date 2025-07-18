"""
v1.4
filingSplitPages can now takes a list of possible pages seperator


v1.3

handle case filing is only 2 pages or less

updating regex in filingSplitPages
new function to associate pages of a filing to each element of a list

v1.2.1
searchPagesForPatterns will return -1 if empty

v1.2
added another example of use

"filingSplitPages" now case insensitive
"searchPagesForPatterns" can search html or only text for patterns

v1.1
filingSplitPages now return a list of tuple (page #, page content)

some adjust to savePagesTuples saved file name
 
v1.0

"""

# from a sec filing, split into pages and search each pages for wanted pattern


# import requests
import requests

#import beautiful soup
from bs4 import BeautifulSoup


#import regular expression
import re

import os

headers = {"User-Agent": "Mozilla/5.0"}

# from online edgar filing, split it into pages, return a list of tuple (page number, page content in html)
def filingSplitPages(address, listPageSeparators=None):
   
    # default separator argument
    if listPageSeparators is None:
        listPageSeparators = ["(<[^/].*?(page-break-(after|before):\s?always(.*?>)))",
                              "(<[^/].*?break-before:\s?page(.*?>))"]

    # access edgar to get the filing
    response = requests.get(url = address, headers = headers)
    
    edgar_str = response.content

    soup = BeautifulSoup(edgar_str, "lxml")
    soupStr = str(soup)
    
    # search filing for page breaks
    if len(listPageSeparators) == 1:
        rw = re.compile(listPageSeparators[0], re.IGNORECASE)
    else:
        rw = re.compile('|'.join(listPageSeparators), re.IGNORECASE)
    
    filingSplit = re.finditer(rw, soupStr)

    starts = []

    for f in filingSplit:
        starts.append(f.start())
        
    if len(starts)== 0:
        print("No pages delimiters founds.")
        return -1
    
    # build list with pages
    filing = []

    #filing with only 2 pages
    if len(starts) == 1:
        
        filing.append((0, soupStr[0:starts[0]]))
        filing.append((1, soupStr[starts[0]:]))

        return filing


    #first page
    filing.append((0, soupStr[0:starts[0]]))

    #all other pages before last page
    y = len(starts)
    x = range(1,y)
    
    for n in x:
        filing.append((n, soupStr[starts[n-1]:starts[n]]))

    #last page
    filing.append((y, soupStr[starts[n]:]))
    
    return filing

# for each pages of a filing, search for patterns, return a list of tuples (page #, page content)
def searchPagesForPatterns(listPages, listWanted, listUnwanted, textOnly = False):
    
    relevantPages = []
    relevant = False

    # build regex
    
    if len(listWanted) == 1:
        rW = re.compile(listWanted[0], re.IGNORECASE)
    else:
        rW = re.compile('|'.join(listWanted), re.IGNORECASE)
    
    
    if len(listUnwanted) == 1:
        rU = re.compile(listUnwanted[0], re.IGNORECASE)
    else:
        rU = re.compile('|'.join(listUnwanted), re.IGNORECASE)
    
 
    
    # for each page of a filing
    for r in listPages:

        if textOnly:
            soup = BeautifulSoup(r[1], "lxml")
            dummy = soup.get_text()
        else:
            dummy = r[1]

        # search for wanted pattern
        if re.search(rW, dummy):
            relevant = True
        
        # save those pages
        if relevant:
            relevantPages.append((r[0], r[1]))
        
        # stop when we find an unwanted pattern
        if re.search(rU, dummy):
            relevant = False
        
       
    if len(relevantPages) == 0:
        return -1
    else:
        return relevantPages

# associate pages of a filings to each  elements of a list, return a dictionary key: element of the list; value: list of pages
def associateFilingPagesToElements(filingPages, listElement, textOnly = False,  saveToDisk = False):

   
    fundPages = {}
    
    for f in listElement:
    
        unwanted = []
        wanted =[f]
        
        for f1 in listElement:
            if f1 != f:
                unwanted.append(f1)
    
    
        relevantPages = searchPagesForPatterns(filingPages, wanted, unwanted, textOnly)
    
        if relevantPages != -1: 
    
            pages = []
    
            for p in relevantPages:
                pages.append(p[0])
    
            fundPages[wanted[0]] = pages

            if saveToDisk:
                savePagesTuples(relevantPages, wanted[0])
            
        else:
            print(f"Couldn't find {wanted[0]}")

    if len(fundPages) == 0:
        return -1
    else:
        return fundPages


        

# save a list of pages tuple into disk
def savePagesTuples(pagesTuples, directory):
    
    path = directory
    
    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)
    
    for p in pagesTuples:

        fileName = path + "/" + str(p[0]) + "_" + str(directory) + ".htm"

        with open(fileName, 'w', encoding='utf-8') as f:
            f.write(p[1])

            
# usage example 
if __name__ == "__main__":

    # using not default page separator
    report = filingSplitPages("https://www.sec.gov/Archives/edgar/data/27825/000120677409000698/delagrpincomefunds_ncsr.htm", ['<hr align="center" noshade="" size="2" width="100%"/>'])
    savePagesTuples(report, "testNCSR2")

    #look for pages related to 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'
    report = filingSplitPages("https://www.sec.gov/Archives/edgar/data/1651872/000113542823000017/mondrian-ncsr.htm")
    
    # patterns we are searching for
    listW = ['MONDRIAN INTERNATIONAL VALUE EQUITY FUND']
    
    # patterns to stop search
    listU = ['MONDRIAN EMERGING MARKETS VALUE EQUITY FUND', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND', 'Mondrian Global Equity Value Fund']
    
    # search each pages
    testF = searchPagesForPatterns(report, listW, listU)
    
    # save on disk
    savePagesTuples(testF, "testNCSR")

    # gets pages with "table"
    testTables = searchPagesForPatterns(testF, ["<table"], ["</table>"])
    savePagesTuples(testTables, "testTables")

    # extracting PIS from Delaware Ivy Core Equity Fund 485bpos
    listWIvy = ["Delaware Ivy Core Equity Fund"]
    listUIvy = ["Delaware Ivy Systematic Emerging Markets Equity Fund", "Delaware Ivy Balanced Fund", "Delaware Ivy Asset Strategy Fund", "Delaware Climate Solutions Fund"]

    report485 = filingSplitPages("https://www.sec.gov/Archives/edgar/data/883622/000114544322000221/dif-20220331.htm")

    # search report for pages on Delaware Ivy Core Equity Fund
    pages485 = searchPagesForPatterns(report485, listWIvy, listUIvy, True)
    savePagesTuples(pages485, "test485")

    # search pages on Delaware Ivy Core Equity Fund for PIS
    pagesPIS = searchPagesForPatterns(pages485, ["principal investment strategies"], ["principal risks of investing", "risks of investing"], True)
    savePagesTuples(pagesPIS, "testPIS")


    #associate pages of a filing to each funds inside
    listElement = ['Invesco Income Advantage U.S. Fund',
                    'Invesco Floating Rate ESG Fund',
                    'Invesco Global Real Estate Income Fund',
                    'INVESCO CORE PLUS BOND FUND',
                    'INVESCO EQUITY AND INCOME FUND',
                    'INVESCO GROWTH AND INCOME FUND',
                    'INVESCO EQUALLY-WEIGHTED S&P 500 FUND',
                    'INVESCO S&P 500 INDEX FUND',
                    'INVESCO AMERICAN FRANCHISE FUND',
                    'Invesco Short Duration High Yield Municipal Fund',
                    'Invesco Short Term Municipal Fund',
                    'Invesco Senior Floating Rate Fund',
                    'Invesco Capital Appreciation Fund',
                    'Invesco Discovery Fund',
                    'Invesco Master Loan Fund',
                    'Invesco Nasdaq 100 Index Fund']
    
    filingPages = filingSplitPages("https://www.sec.gov/Archives/edgar/data/1112996/000119312522277504/d402614dncsr.htm")
    fundPages = associateFilingPagesToElements(filingPages, listElement, True, True)
    
    for x, y in fundPages.items():
        print(x, y)