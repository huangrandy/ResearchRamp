from concurrent.futures import ThreadPoolExecutor
import json


def query_seminal_works(survey_papers, gpt_agent):
    """
    Query for seminal works for each paper in the survey papers.
    """
    seminal_paper_counts_by_topic = {}
    top_references = {}

    def find_seminal_works(concept, paper):
        title = paper.get("title", "Unknown Title")
        input_text = f"""
        For the paper titled '{title}', provide the 5 most seminal works (including papers and textbooks) in the field that are related to this paper and would likely be cited. 
        If you cannot access external databases, respond with 5 hypothetical seminal works based on the paper title in the following example JSON format (not with this content, but with the same structure):
        Do NOT include tick marks or any other formatting. Just ONLY provide the JSON object: 
        {{
            "seminal_works": [
                {{"title": "Seminal Work 1", "year": 1998}},
                {{"title": "Seminal Work 2", "year": 2013}},
                {{"title": "Seminal Work 3", "year": 2015}},
                {{"title": "Seminal Work 4", "year": 2020}},
                {{"title": "Seminal Work 5", "year": 2021}}
            ]
        }}
        """
        try:
            gpt_response = gpt_agent.query("You are a helpful assistant.", input_text)
            references = json.loads(gpt_response).get("seminal_works", [])
            return concept, title, references
        except json.JSONDecodeError:
            print(f"Failed to parse GPT-4 response for paper: {title}")
            return concept, title, []

    with ThreadPoolExecutor() as executor:
        future_to_paper = {
            executor.submit(find_seminal_works, concept, paper): (concept, paper)
            for concept, papers in survey_papers.items()
            for paper in papers.get("papers", [])
        }
        for future in future_to_paper:
            concept, title, references = future.result()
            if concept not in top_references:
                top_references[concept] = {}
            if concept not in seminal_paper_counts_by_topic:
                seminal_paper_counts_by_topic[concept] = {}

            top_references[concept][title] = references
            for ref in references:
                ref_title = ref["title"]
                if ref_title in seminal_paper_counts_by_topic[concept]:
                    seminal_paper_counts_by_topic[concept][ref_title] += 1
                else:
                    seminal_paper_counts_by_topic[concept][ref_title] = 1

    return seminal_paper_counts_by_topic, top_references
