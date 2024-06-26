import os
import json
from typing import List

from paper import Paper

class Project:
    def __init__(self, name: str):
        self.name = name
        self.papers: List[Paper] = []
        self.data = { }

        file_name = f'projects/{name}.json'
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                data = json.load(f)
                self.load_papers(data["papers"])

    def load_papers(self, papers: List[str]):
        for arxiv_id in papers:
            self.papers.append(Paper(arxiv_id))

    def save(self):
        if not os.path.exists('projects'):
            os.mkdir('projects')
        with open(f'projects/{self.name}.json', 'w') as f:
            obj = self.to_obj()
            papers = []
            for paper in obj["papers"]:
                papers.append(paper['arxiv_id'])
            obj["papers"] = papers
            json.dump(obj, f, indent=4)

    def add_paper(self, paper_id: str) -> bool:
        paper = Paper(paper_id)
        containsPaper = False
        for p in self.papers:
            if p.arxiv_id == paper_id:
                containsPaper = True
                break
        if containsPaper:
            return False
        
        self.papers.append(paper)
        return True
    
    def remove_paper(self, paper_id: str):
        paper = None
        for p in self.papers:
            if p.arxiv_id == paper_id:
                paper = p
                break
        self.papers.remove(paper)

    def to_obj(self):
        papers = []
        for p in self.papers:
            papers.append(p.to_obj())
        return {
            "name": self.name,
            "papers": papers
        }

def get_projects() -> List[Project]:
    projects = []
    if not os.path.exists('projects'):
        return []
    for p in os.listdir('projects'):
        projects.append(Project(p.replace('.json', '')))
    return projects
