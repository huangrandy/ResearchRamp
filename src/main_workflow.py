import os
import json
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
from agents.general_agent import Agent
from agents.seminal_eval_agent import SeminalEvalAgent
from agents.concept_extraction_agent import ConceptExtractionAgent
from utils.tree_builder import build_tree_graph
from utils.visualization import visualize
from utils.survey_papers import query_survey_papers
from utils.seminal_works import query_seminal_works
from utils.prune_papers import prune_papers
from utils.foundational_topics import find_foundational_topics_and_resources
import sys
from dotenv import load_dotenv

load_dotenv() 


def extract_project_concepts(project, concept_agent):
    """
    Extract project concepts using the concept extraction agent.
    """
    try:
        print("Extracting concepts from the project...")
        response = concept_agent.extract_concepts(f"{project}.json")
        return (
            response["project_title"],
            response["project_summary"],
            response["core_concepts"],
            response["specialized_concepts"],
            response["fundamental_concepts"],
            response["prerequisites"],
        )
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return None, None, None, None, None, None


def main(project="robotics"):
    # Setup
    notebook_dir = os.path.dirname(os.path.abspath(__file__))
    queries_folder = os.path.abspath(os.path.join(notebook_dir, "..", "queries"))
    gpt_agent = Agent(api_key=os.getenv("OPENAI_API_KEY"))
    concept_agent = ConceptExtractionAgent(gpt_agent, queries_folder=queries_folder)

    # Step 1: Extract project concepts
    project_title, project_summary, core_concepts, specialized_concepts, fundamental_concepts, prerequisites = extract_project_concepts(
        project, concept_agent
    )
    if not project_title:
        return

    # Step 2: Query survey papers
    survey_papers = query_survey_papers(core_concepts, gpt_agent)
    print("\nSurvey Papers:")
    for concept, papers in survey_papers.items():
        print(f"\nConcept: {concept}")
        for paper in papers.get("papers", []):
            print(f"- {paper['title']}")

    # Step 3: Query seminal works
    seminal_paper_counts_by_topic, top_references = query_seminal_works(survey_papers, gpt_agent)
    print("\nSeminal Paper Counts by Topic:")
    for concept, counts in seminal_paper_counts_by_topic.items():
        print(f"\nConcept: {concept}")
        sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        for paper_title, count in sorted_counts:
            print(f"{paper_title}: {count}")

    # Step 4: Select papers for evaluation
    seminal_eval_agent = SeminalEvalAgent(seminal_paper_counts_by_topic, gpt_agent, project_summary)
    selected_papers = seminal_eval_agent.select_papers()
    print("\nSelected Papers for Evaluation:")
    for topic, papers in selected_papers.items():
        print(f"\nTopic: {topic}")
        for paper in papers:
            print(f"- {paper}")

    # Step 5: Prune selected papers
    pruned_selected_papers = prune_papers(specialized_concepts, selected_papers, gpt_agent, project_summary)
    pprint(pruned_selected_papers)
    print("\nPruned Selected Papers for Evaluation:")
    for topic, papers in pruned_selected_papers.items():
        print(f"\nTopic: {topic}")
        for paper in papers:
            print(f"- {paper}")

    # Step 6: Find foundational topics and resources
    final_foundational_topics = find_foundational_topics_and_resources(
        pruned_selected_papers, fundamental_concepts, gpt_agent, core_concepts
    )
    print("\nFinal Foundational Topics and Recommended Resources:")
    for paper, topics in final_foundational_topics.items():
        print(f"\nPaper: {paper}")
        for topic in topics:
            print(f"- {topic['topic']}: {topic.get('resource', 'No resource available')}")

    # Step 7: Build and visualize the tree graph
    G = build_tree_graph(
        project_title,
        core_concepts,
        pruned_selected_papers,
        final_foundational_topics,
    )
    visualize(G)


if __name__ == "__main__":
    project = sys.argv[1] if len(sys.argv) > 1 else "robotics"
    main(project)
