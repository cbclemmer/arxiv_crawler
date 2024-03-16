import os
import re
import json
import shutil
import tarfile
import gzip
from typing import List

import requests
import bibtexparser

from lib import Reference

def get_source_file_name(paper_id: str):
    return 'source/' + paper_id.replace('.', '')

def download_arxiv(paper_id: str):
    source_file_name = get_source_file_name(paper_id)
    url = f'https://arxiv.org/e-print/{paper_id}'
    response = requests.get(url)
    if response.status_code == 404:
        print(f'Error reading source: recieved 404 for {url}')
        return None
    if response.status_code != 200:
        raise Exception(f'Error downloading source code for paper {paper_id}\n{response.content.decode()}')
    print('Found paper source code, parsing file')
    if not os.path.exists('source'):
        os.mkdir('source')
    with open(source_file_name, 'wb') as f:
        f.write(response.content)
    return True

def unzip(paper_id: str):
    source_file_name = get_source_file_name(paper_id)
    with gzip.open(source_file_name) as f:
        gzip_file = f.read()
        gzip.decompress(gzip_file)
        os.remove(source_file_name)
        with open(source_file_name, 'wb') as f:
            f.write(source_file_name)

# def get_arxiv_from_g_scholar(title: str):


def get_references_for_file(file_name: str):
    references = []
    with open(file_name, 'r') as f:
        library = bibtexparser.bparser.parse(f.read())
        for entry in library.entries:
            ref = Reference()
            ref.bib_data = entry
            if 'journal' in entry:
                journal: str = entry["journal"]
                match = re.findall('arxiv:\d{4}.\d{5}', journal.lower())
                if len(match) != 0:
                    ref.arxiv_id = match[0].split('arxiv:')[1]
            # if ref.arxiv_id is None and 'title' in ref.bib_data:
            #     ref.arxiv_id = get_arxiv_from_g_scholar(ref.bib_data["title"])
            references.append(ref)
    return references

def get_references(paper_id: str) -> List[str]:
    paper_id = paper_id.replace('.', '')
    cleaned_id = paper_id
    source_file_name = f'source/{paper_id}'
    references_file_name = f'references/{cleaned_id}.json'

    if not os.path.exists('source'):
        os.mkdir('source')

    if not os.path.exists('references'):
        os.mkdir('references')

    if os.path.exists(references_file_name):
        with open(references_file_name, 'r') as f:
            return json.load(f)
    
    if not os.path.exists(source_file_name):
        print('Attempting to download source')
        res = download_arxiv(paper_id)
        if res is None:
            return None # Bail if not downloaded
    
    if os.path.exists('tmp'):
        shutil.rmtree('tmp')
    os.mkdir('tmp')

    try:
        if not tarfile.is_tarfile(source_file_name):
            unzip(paper_id) # Unzip to tar file
        
        if not tarfile.is_tarfile(source_file_name):
            print('Error reading source: unzipped data is not a tarball')
            os.rmdir('tmp')
            return None # Bail if not tarfile
        
        with tarfile.open(source_file_name) as tar:
            tar.extractall(path='tmp', filter='data')
        
        references = []
        for file in os.listdir('tmp'):
            if '.bib' in file:
                for reference in get_references_for_file('tmp/' + file):
                    references.append(reference)

        reference_file_data = []
        for reference in references:
            reference_file_data.append(reference.to_obj())
        with open(references_file_name, 'w') as f:
            json.dump(reference_file_data, f, indent=4)    
    finally:
        shutil.rmtree('tmp')
    return references