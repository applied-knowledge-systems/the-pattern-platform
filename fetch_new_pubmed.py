import requests
import json
import xmltodict 

db = 'pmc'
domain = 'https://www.ncbi.nlm.nih.gov/entrez/eutils'
nresults = 4
query = "biosynthetic+gene+clusters"
retmode='json'

# standard query
queryLinkSearch = f'{domain}/esearch.fcgi?db={db}&retmax={nresults}&retmode={retmode}&term={query}&usehistory=y'
response = requests.get(queryLinkSearch)
pubmedJson = response.json()

results = []

for paperId in pubmedJson["esearchresult"]["idlist"]:
    # metadata query
    # queryLinkSummary = f'{domain}/esummary.fcgi?db={db}&id={paperId}&retmode={retmode}'
    # print(queryLinkSummary)
    fetch_abstract=f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db={db}&id={paperId}&retmode=xml&rettype=abstract'
    print(fetch_abstract)
    print(f'article_id:PMC{paperId}')
    my_pmc_dict=xmltodict.parse(requests.get(fetch_abstract).content)
    if '#text' in my_pmc_dict['pmc-articleset']['article']['front']['article-meta']['title-group']['article-title']:
        title=my_pmc_dict['pmc-articleset']['article']['front']['article-meta']['title-group']['article-title']['#text']
    else:
        title=my_pmc_dict['pmc-articleset']['article']['front']['article-meta']['title-group']['article-title']
    print(f'article_id:PMC{paperId}:{title}')
    print(my_pmc_dict['pmc-articleset']['article']['front']['article-meta']['pub-date'][0])
    article_body=[]
    if '#text'in my_pmc_dict['pmc-articleset']['article']['front']['article-meta']['abstract']['p']:
        article_body.append(my_pmc_dict['pmc-articleset']['article']['front']['article-meta']['abstract']['p']['#text'])
    else:
        article_body.append(my_pmc_dict['pmc-articleset']['article']['front']['article-meta']['abstract']['p'])

    print(f'paragraphs:PMC{paperId}'," ".join(article_body))