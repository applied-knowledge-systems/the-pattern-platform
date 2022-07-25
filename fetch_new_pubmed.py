import requests
import json
import xmltodict

db = 'pmc'
domain = 'https://www.ncbi.nlm.nih.gov/entrez/eutils'
nresults = 2
query = "depression"
retmode='json'

# standard query
queryLinkSearch = f'{domain}/esearch.fcgi?db={db}&retmax={nresults}&retmode={retmode}&term={query}+AND+open+access[filter] '
response = requests.get(queryLinkSearch)
pubmedJson = response.json()

results = []

for paperId in pubmedJson["esearchresult"]["idlist"]:
    # metadata query
    queryLinkSummary = f'{domain}/esummary.fcgi?db={db}&id={paperId}&retmode={retmode}'
    print(f'{queryLinkSummary}')
    results.append({'paperId': paperId, 'metadata': requests.get(queryLinkSummary).json()})
    
    # check the journalnames 
    print(results[-1]["metadata"]["result"][paperId]["fulljournalname"])
    for article_id in results[-1]["metadata"]["result"][paperId]["articleids"]:
        print(article_id)
        if article_id["idtype"]=="pmcid":
            print(article_id["value"])
            article_full=requests.get(f'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={article_id["value"]}').text
            print(article_full)
            dict_data = xmltodict.parse(article_full)
            print(dict_data['OA']['records']['record']['link']['@href'])

resultsSorted = sorted(results, key=lambda x: x["metadata"]["result"][x["paperId"]]["fulljournalname"])

# with open('resultsSorted.json', 'w') as f:
#     json.dump(resultsSorted, f)
# FIXME: add fetch, unzip and parse https://github.com/titipata/pubmed_parser
#  paragraphs=pp.parse_pubmed_paragraph('PMC9303145/ECAM2022-3586290.nxml')
# join section and text paragraphs[0]['text']
# pp.parse_pubmed_xml('PMC9303145/ECAM2022-3586290.nxml') to get publication date
