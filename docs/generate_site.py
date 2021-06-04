import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter
import csv

books = []

for file in Path("data").glob("*md"):
    
    book = {}
    
    connection = open(file, "r")
    
    book['id'] = str(file).replace('data/', '').replace('.md', '')
    book['text'] = connection.read()
    
    books.append(book)

metadata = {}
 
filename = "metadata.tsv"
  
with open(filename, 'r') as meta_tsv:
      
    for line in csv.DictReader(meta_tsv, delimiter="\t"):
        
        dictionary = dict(line)
        
        metadata[dictionary['handle'].replace("http://fennougrica.kansalliskirjasto.fi/handle/", '').replace('/', '_')] = dictionary


for book in books:
    
    try:

        book['metadata'] = metadata[book['id']]
        
    except:
        
        print(f"Check {book['id']}")

for book in books:
    
    start_block = f"""---
title: "{book['metadata']['title_cyr']}"
output:
  html_document:
    css: "style.css"
    toc: true
    toc_float: true
---
"""
    
    filename = book['metadata']['handle'].replace('http://fennougrica.kansalliskirjasto.fi/handle/', '').replace('/', '_')
    
    file = open(f"{filename}.Rmd", "w")
    
    description_block = f"""
    
## Cite as
    
```
@book{{{filename},
author={{{book['metadata']['author_cyr']}}},
year={{{book['metadata']['year']}}},
title={{{book['metadata']['title_cyr']}}},
url={{{book['metadata']['handle']}}},
note={{Scanned in the National Library of Finland's Fenno-Ugrica project. Processed and proofread by {book['metadata']['proofreader']}. Selected and organized into Written Komi Corpus: Fenno-Ugrica collection by Niko Partanen.}}
}}
```
"""
    
    text = ''

    for line in book['text'].split("\n"):
        
        if line.isupper() and "#" not in line:
            
            text += f"### {line.title()}\n"
        
        else:
            
            text += f"{line}\n"
        

    file.write(start_block)
    file.write(text)

    file.write(description_block)
    
    file.close()

titles = []

for book in books:
    
    entry = {}
    
    filename = book['metadata']['handle'].replace('http://fennougrica.kansalliskirjasto.fi/handle/', '').replace('/', '_')
    
    entry['category'] = book['metadata']['categories_eng'] 
    entry['title'] = book['metadata']['title']
    entry['file'] = filename
    
    titles.append(entry)
    
titles_sorted = sorted(titles, key = lambda i: i['category'])

yaml = open("_site.yml", "w")

yaml_start = """
name: "Written Komi Corpus: Fenno-Ugrica"
output_dir: "docs"
navbar:
  title: "Fenno-Ugrica Corpus"
  left:
    - text: "Home"
      href: index.html
"""

yaml.write(yaml_start)

current_category = "Agriculture"

s = "  "

yaml.write(f"{s}{s}- text: \"{current_category}\"\n")
yaml.write(f"{s}{s}{s}menu:\n")

for title in titles_sorted:
        
    if title['category'] == current_category:
        
        yaml.write(f"{s}{s}{s}{s}- text: \"{title['title']}\"\n")
        yaml.write(f"{s}{s}{s}{s}{s}href: {title['file']}.html\n")
    
    else:
        
        yaml.write(f"{s}{s}- text: \"{title['category']}\"\n")
        yaml.write(f"{s}{s}{s}menu:\n")
        yaml.write(f"{s}{s}{s}{s}- text: \"{title['title']}\"\n")
        yaml.write(f"{s}{s}{s}{s}{s}href: {title['file']}.html\n")
        current_category = title['category']
        
yaml_end = """    - text: "About"
      href: about.html
"""

yaml.write(yaml_end)

yaml.close()

print("Rendering site")

os.system("R -e 'library(rmarkdown);library(knitr);rmarkdown::render_site()'")
