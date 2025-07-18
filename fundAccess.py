"""""
v1.9
added the cases of N-CSR filings

v1.8
extract form infos

only searchEdgarFund is relevant, just keep the other there


v1.7
more accurate on filing type

v1.6
searchEdgarFund will take now use a edgar fund series or class number

v1.5
now returns a edgarFiling object

v1.4
move filingSplitPages to another python file

v1.3
list of all funds in a filing now include serie number

v1.2
will now list all funds in a filing

v1.1
can now split filing into pages

v1.1
return tuple with filing date

v1.0

"""

# find edgar link to specific filings of a fund

# import requests
import requests

# import beautiful soup
from bs4 import BeautifulSoup

# import json
import json

# import regular expression
import re

headers = {"User-Agent": "Mozilla/5.0"}

class edgarFiling:

    def __init__(self, edgarId, filing, filingDate, link, form, listFunds):
        self.edgarId = edgarId
        self.filing = filing
        self.filingDate = filingDate
        self.link = link
        self.listFunds = listFunds
        self.form = form

class ncsrFiling:

    def __init__(self, edgarFiling):

        self.edgarId = edgarFiling.edgarId
        self.filing = edgarFiling.filing
        self.link = edgarFiling.link
        self.listFunds = edgarFiling.listFunds
        self.form = edgarFiling.form

        for f in edgarFiling.listFunds:
            if f[0] == edgarFiling.edgarId:
                self.name = f[1]
                break

        dummyForm = [line for line in edgarFiling.form.split('\n') if line.strip()]

        for i in range(len(dummyForm)):

            if "SEC Accession No" in dummyForm[i]:
                self.accessionNo = dummyForm[i].split()[-1]

            if dummyForm[i] == "Filing Date":
                self.filingDate = dummyForm[i+1]

            if dummyForm[i] == "Accepted":
                self.acceptedDate = dummyForm[i+1]

            if dummyForm[i] == "Documents":
                self.documents = dummyForm[i+1]

            if dummyForm[i] == "Period of Report":
                self.reportingDate = dummyForm[i+1]
        
            if dummyForm[i] == "Effectiveness Date":
                self.effectivenessDate = dummyForm[i+1]

# function safe to ignore
# run this first !!!!
# get some data from edgar
def edgarFundData():

    response = requests.get(url = "https://www.sec.gov/files/company_tickers_mf.json", headers = headers)
    
    data = json.loads(response.text)
    
    return data

# function safe to ignore
# from a ticker, return cik, series and class number
def mapTicker(ticker, fundData):
    
    for fund in fundData["data"]:
        
        if fund[3] == ticker:
            return fund

    return -1

# from the inputed series, go to the desired filings in edgar
def searchEdgarFund(edgarId, filing, count):

    # build the edgar query
    endpoint = r"https://www.sec.gov/cgi-bin/browse-edgar" #base url

    # build search parameters
    param_dict = {
                 "action": "getcompany",
                 "CIK": edgarId,
                 "type": filing,
                 "count": count
                  }


    # edgar search
    #headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url=endpoint, params = param_dict, headers = headers)
    #print(response.url)
    edgar_str = response.text

    # find links to the filings
    soupFilingLinks = BeautifulSoup(edgar_str, "html.parser")

    table_tag = soupFilingLinks.find('table', class_='tableFile2')
    rows = table_tag.find_all('tr')

    filingLinks = []
    filingDates = []
    filingTypes = []

    for row in rows:

        cells = row.find_all("td")

        if len(cells) > 3:
           #print(cells[1].a["href"])
           filingLinks.append("https://www.sec.gov" + cells[1].a["href"])
           filingDates.append(cells[3].text)
           filingTypes.append(cells[0].text)

    #print(filingLinks)
    #print(filingDates)

    # access each filing
    docLinks = []
    otherFunds = []
    listForms = []

    for link in filingLinks:

        page = requests.get(link, headers = headers)
        pages = page.text

        soupPage = BeautifulSoup(pages, 'html.parser')
        table_tag = soupPage.find("table", class_="tableFile", summary="Document Format Files")
        rows = table_tag.find_all("tr")

        # find all form infos
        listForms.append(soupPage.find("div", id="formDiv").text.strip())
        

        # find all funds in a filing
        cik_tag = soupPage.find_all("td", class_= "seriesName")
        otherFundsNames = []

        for c in cik_tag:
            f = (c.a.text, c.next_sibling.next_sibling.next_sibling.next_sibling.text)
            otherFundsNames.append(f)

        otherFunds.append(otherFundsNames)

        # get the link to access the filing
        for row in rows:

            cells = row.find_all("td")

            if(len(cells) > 3):

                    if filing in cells[3].text:
                        doc = "https://www.sec.gov" + cells[2].a["href"]
                        #print(cells[2].a["href"])
                        docLinks.append(doc)
                    else:
                        pass

        #time.sleep(1) #in case you reach edgar queries limit per second

    #print(docLinks)

    res = []

    for date, f, link, form, other in zip(filingDates, filingTypes, docLinks, listForms, otherFunds):
        res.append(edgarFiling(edgarId, f, date, link, form, other))

    return res


def searchEdgarNCSR(edgarId, count, filing = ["N-CSR", "N-CSR/A", "N-CSRS", "N-CSRS/A"]):

    listNCSR = searchEdgarFund(edgarId, "N-CSR", count)

    results = []

    for r in listNCSR:
        if r.filing in filing:
            results.append(ncsrFiling(r))

    return results



# usage example
if __name__ == "__main__":
    
    print("Access the 10 latest N-CSR of Mondrian International Value Equity Fund using series id S000051620")

    s = "S000051620"

    print("Search  for N-CSR with series number")
    res = searchEdgarFund(s, "N-CSR", 10)

    for r in res:
        print(f"id: {r.edgarId} filing: {r.filing} date: {r.filingDate} link: {r.link} list funds: {r.listFunds}")
        print(":::")
        print(r.form)
        print("===============\n")

    print("Search  for 485bpos with series id")
    res = searchEdgarFund(s, "485", 10)

    # print the form field
    for r in res:
        print(f"id: {r.edgarId} filing: {r.filing} date: {r.filingDate} link: {r.link} list funds: {r.listFunds}")
        print(":::")
        print(r.form)
        print("===============\n")

"""
H:\Python\python.exe "H:/Python Project/pythonProject/test_api_2/fundAccess.py"
Access the 10 latest N-CSR of Mondrian International Value Equity Fund using series id S000051620
Search  for N-CSR with series number
id: S000051620 filing: N-CSR date: 2024-01-09 link: https://www.sec.gov/Archives/edgar/data/1651872/000139834424000360/fp0086430-1_ncsr.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form N-CSR - Certified Shareholder Report: 
      

SEC Accession No. 0001398344-24-000360
      



Filing Date
2024-01-09
Accepted
2024-01-09 15:11:43
Documents
47


Period of Report
2023-10-31
Effectiveness Date
2024-01-09
===============

id: S000051620 filing: N-CSRS date: 2023-07-07 link: https://www.sec.gov/Archives/edgar/data/1651872/000114036123033728/mondrian-43023-ncsrs.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form N-CSRS - Certified Shareholder Report, Semi-Annual: 
      

SEC Accession No. 0001140361-23-033728
      



Filing Date
2023-07-07
Accepted
2023-07-07 15:20:56
Documents
10


Period of Report
2023-04-30
Effectiveness Date
2023-07-07
===============

id: S000051620 filing: N-CSR date: 2023-01-09 link: https://www.sec.gov/Archives/edgar/data/1651872/000113542823000017/mondrian-ncsr.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form N-CSR - Certified Shareholder Report: 
      

SEC Accession No. 0001135428-23-000017
      



Filing Date
2023-01-09
Accepted
2023-01-09 12:56:25
Documents
15


Period of Report
2022-10-31
Effectiveness Date
2023-01-09
===============

id: S000051620 filing: N-CSRS date: 2022-07-11 link: https://www.sec.gov/Archives/edgar/data/1651872/000113542822000061/mondrian-ncsrs.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form N-CSRS - Certified Shareholder Report, Semi-Annual: 
      

SEC Accession No. 0001135428-22-000061
      



Filing Date
2022-07-11
Accepted
2022-07-11 13:15:20
Documents
11


Period of Report
2022-04-30
Effectiveness Date
2022-07-11
===============

id: S000051620 filing: N-CSR date: 2022-01-07 link: https://www.sec.gov/Archives/edgar/data/1651872/000113542822000015/mondrian103121ar.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form N-CSR - Certified Shareholder Report: 
      

SEC Accession No. 0001135428-22-000015
      



Filing Date
2022-01-07
Accepted
2022-01-07 12:44:02
Documents
17


Period of Report
2021-10-31
Effectiveness Date
2022-01-07
===============

id: S000051620 filing: N-CSRS date: 2021-07-08 link: https://www.sec.gov/Archives/edgar/data/1651872/000113542821000067/gallery043021ncsrs.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form N-CSRS - Certified Shareholder Report, Semi-Annual: 
      

SEC Accession No. 0001135428-21-000067
      



Filing Date
2021-07-08
Accepted
2021-07-08 13:10:48
Documents
10


Period of Report
2021-04-30
Effectiveness Date
2021-07-08
===============

id: S000051620 filing: N-CSR date: 2021-01-08 link: https://www.sec.gov/Archives/edgar/data/1651872/000113542821000003/gallery103120ncsr.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form N-CSR - Certified Shareholder Report: 
      

SEC Accession No. 0001135428-21-000003
      



Filing Date
2021-01-08
Accepted
2021-01-08 16:02:28
Documents
17


Period of Report
2020-10-31
Effectiveness Date
2021-01-08
===============

id: S000051620 filing: N-CSRS date: 2020-07-08 link: https://www.sec.gov/Archives/edgar/data/1651872/000113542820000100/gallery-ncsrs-4-30-20.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000063815', 'ROTHKO EMERGING MARKETS EQUITY FUND')]
:::
Form N-CSRS - Certified Shareholder Report, Semi-Annual: 
      

SEC Accession No. 0001135428-20-000100
      



Filing Date
2020-07-08
Accepted
2020-07-08 13:39:26
Documents
11


Period of Report
2020-04-30
Effectiveness Date
2020-07-08
===============

id: S000051620 filing: N-CSR date: 2020-01-08 link: https://www.sec.gov/Archives/edgar/data/1651872/000113542820000008/mondrian10312019ar.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000063815', 'ROTHKO EMERGING MARKETS EQUITY FUND')]
:::
Form N-CSR - Certified Shareholder Report: 
      

SEC Accession No. 0001135428-20-000008
      



Filing Date
2020-01-08
Accepted
2020-01-08 17:01:43
Documents
18


Period of Report
2019-10-31
Effectiveness Date
2020-01-08
===============

id: S000051620 filing: N-CSRS date: 2019-07-09 link: https://www.sec.gov/Archives/edgar/data/1651872/000113542819000058/gallery-ncsrs.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000063815', 'ROTHKO EMERGING MARKETS EQUITY FUND')]
:::
Form N-CSRS - Certified Shareholder Report, Semi-Annual: 
      

SEC Accession No. 0001135428-19-000058
      



Filing Date
2019-07-09
Accepted
2019-07-09 14:52:48
Documents
11


Period of Report
2019-04-30
Effectiveness Date
2019-07-09
===============

Search  for 485bpos with series id
id: S000051620 filing: 485BPOS date: 2023-02-28 link: https://www.sec.gov/ix?doc=/Archives/edgar/data/1651872/000139834423005186/fp0082231-1_485bpos.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form 485BPOS - Post-effective amendment [Rule 485(b)]: 
      

SEC Accession No. 0001398344-23-005186
      



Filing Date
2023-02-28
Accepted
2023-02-28 16:55:55
Documents
32


Effectiveness Date
2023-02-28
===============

id: S000051620 filing: 485BPOS date: 2023-02-28 link: https://www.sec.gov/ix?doc=/Archives/edgar/data/1651872/000139834423005186/fp0082231-1_485bpos.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form 485BPOS - Post-effective amendment [Rule 485(b)]: 
      

SEC Accession No. 0001398344-23-005186
      



Filing Date
2023-02-28
Accepted
2023-02-28 16:55:55
Documents
32


Effectiveness Date
2023-02-28
===============

id: S000051620 filing: 485BPOS date: 2022-02-28 link: https://www.sec.gov/ix?doc=/Archives/edgar/data/1651872/000139834422004465/fp0073153_485bpos-ixbrl.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form 485BPOS - Post-effective amendment [Rule 485(b)]: 
      

SEC Accession No. 0001398344-22-004465
      



Filing Date
2022-02-28
Accepted
2022-02-28 17:08:32
Documents
42


Effectiveness Date
2022-02-28
===============

id: S000051620 filing: 485BPOS date: 2022-02-28 link: https://www.sec.gov/ix?doc=/Archives/edgar/data/1651872/000139834422004465/fp0073153_485bpos-ixbrl.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form 485BPOS - Post-effective amendment [Rule 485(b)]: 
      

SEC Accession No. 0001398344-22-004465
      



Filing Date
2022-02-28
Accepted
2022-02-28 17:08:32
Documents
42


Effectiveness Date
2022-02-28
===============

id: S000051620 filing: 485BPOS date: 2021-03-05 link: https://www.sec.gov/Archives/edgar/data/1651872/000139834421005817/fp0062887_485bpos-xbrl.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form 485BPOS - Post-effective amendment [Rule 485(b)]: 
      

SEC Accession No. 0001398344-21-005817
      



Filing Date
2021-03-05
Accepted
2021-03-05 14:47:36
Documents
27


Effectiveness Date
2021-03-05
===============

id: S000051620 filing: 485BPOS date: 2021-03-05 link: https://www.sec.gov/Archives/edgar/data/1651872/000139834421005817/fp0062887_485bpos-xbrl.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form 485BPOS - Post-effective amendment [Rule 485(b)]: 
      

SEC Accession No. 0001398344-21-005817
      



Filing Date
2021-03-05
Accepted
2021-03-05 14:47:36
Documents
27


Effectiveness Date
2021-03-05
===============

id: S000051620 filing: 485BPOS date: 2021-02-26 link: https://www.sec.gov/Archives/edgar/data/1651872/000139834421005036/fp0062509_485bpos.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form 485BPOS - Post-effective amendment [Rule 485(b)]: 
      

SEC Accession No. 0001398344-21-005036
      



Filing Date
2021-02-26
Accepted
2021-02-26 16:12:27
Documents
17


Effectiveness Date
2021-02-28
===============

id: S000051620 filing: 485BPOS date: 2021-02-26 link: https://www.sec.gov/Archives/edgar/data/1651872/000139834421005036/fp0062509_485bpos.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000068924', 'Mondrian Global Equity Value Fund')]
:::
Form 485BPOS - Post-effective amendment [Rule 485(b)]: 
      

SEC Accession No. 0001398344-21-005036
      



Filing Date
2021-02-26
Accepted
2021-02-26 16:12:27
Documents
17


Effectiveness Date
2021-02-28
===============

id: S000051620 filing: 485BPOS date: 2020-03-13 link: https://www.sec.gov/Archives/edgar/data/1651872/000139834420005949/fp0051388_485bpos-xbrl.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000063815', 'ROTHKO EMERGING MARKETS EQUITY FUND')]
:::
Form 485BPOS - Post-effective amendment [Rule 485(b)]: 
      

SEC Accession No. 0001398344-20-005949
      



Filing Date
2020-03-13
Accepted
2020-03-13 10:08:22
Documents
28


Effectiveness Date
2020-03-13
===============

id: S000051620 filing: 485BPOS date: 2020-03-13 link: https://www.sec.gov/Archives/edgar/data/1651872/000139834420005949/fp0051388_485bpos-xbrl.htm list funds: [('S000051620', 'MONDRIAN INTERNATIONAL VALUE EQUITY FUND'), ('S000063083', 'MONDRIAN EMERGING MARKETS VALUE EQUITY FUND'), ('S000063084', 'MONDRIAN INTERNATIONAL GOVERNMENT FIXED INCOME FUND'), ('S000063813', 'MONDRIAN GLOBAL LISTED INFRASTRUCTURE FUND'), ('S000063814', 'MONDRIAN U.S. SMALL CAP EQUITY FUND'), ('S000063815', 'ROTHKO EMERGING MARKETS EQUITY FUND')]
:::
Form 485BPOS - Post-effective amendment [Rule 485(b)]: 
      

SEC Accession No. 0001398344-20-005949
      



Filing Date
2020-03-13
Accepted
2020-03-13 10:08:22
Documents
28


Effectiveness Date
2020-03-13
===============


Process finished with exit code 0


"""
