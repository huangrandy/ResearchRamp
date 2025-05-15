import os
import json
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
from agents.general_agent import Agent
from agents.seminal_eval_agent import SeminalEvalAgent
from agents.concept_extraction_agent import ConceptExtractionAgent
from utils.tree_builder import build_tree_graph
from utils.visualization import visualize


def main():
    # Get the current working directory of the script
    notebook_dir = os.getcwd()
    queries_folder = os.path.join(notebook_dir, "..", "queries")

    gpt_agent = Agent(api_key=os.getenv("OPENAI_API_KEY"))
    concept_agent = ConceptExtractionAgent(gpt_agent, queries_folder=queries_folder)

    project = "robotics"

    try:
        print("Extracting concepts from the project...")
        response = concept_agent.extract_concepts(f"{project}.json")
        project_title = response["project_title"]
        project_summary = response["project_summary"]

        core_concepts = response["core_concepts"]
        specialized_concepts = response["specialized_concepts"]
        fundamental_concepts = response["fundamental_concepts"]
        prerequisites = response["prerequisites"]
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return

    # Query for survey papers for each core concept
    survey_papers = {}

    def find_survey_papers(concept):
        """
        Query the agent for seminal papers for a given concept.
        """
        input_text = f"""
        Provide 6 survey papers on the topic '{concept}' along with their DOI id's, URLs, and other metadata in the following JSON format.
        Do NOT include tick marks or any other formatting. Just ONLY provide the JSON object: 
        {{
            "papers": [
                {{
                    "title": "<title>"
                }}
            ]
        }}
        """
        try:
            gpt_response = gpt_agent.query("You are a helpful assistant.", input_text)
            print(f"Survey papers for {concept}:\n{json.dumps(json.loads(gpt_response), indent=4)}")
            return concept, json.loads(gpt_response)
        except json.JSONDecodeError:
            print(f"Failed to parse GPT-4 response for {concept}. Response: {gpt_response}")
            return concept, []

    print("Surveying for papers...")
    with ThreadPoolExecutor() as executor:
        future_to_concept = {executor.submit(find_survey_papers, concept): concept for concept in core_concepts}
        for future in future_to_concept:
            concept, papers = future.result()
            survey_papers[concept] = papers

    print("\nSurvey Papers:")
    for concept, papers in survey_papers.items():
        print(f"\nConcept: {concept}")
        for paper in papers.get("papers", []):
            print(f"- {paper['title']}")

    # Separate dictionaries for seminal paper counts by topic
    seminal_paper_counts_by_topic = {}
    top_references = {}

    def find_seminal_works(concept, paper):
        """
        Query the agent for the 5 most seminal works for a given paper.
        """
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

    print("\nSeminal Paper Counts by Topic:")
    for concept, counts in seminal_paper_counts_by_topic.items():
        print(f"\nConcept: {concept}")
        sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        for paper_title, count in sorted_counts:
            print(f"{paper_title}: {count}")

    # Initialize the evaluation agent
    seminal_eval_agent = SeminalEvalAgent(seminal_paper_counts_by_topic, gpt_agent, project_summary)

    # Select papers based on the criteria
    selected_papers = seminal_eval_agent.select_papers()

    print("\nSelected Papers for Evaluation:")
    for topic, papers in selected_papers.items():
        print(f"\nTopic: {topic}")
        for paper in papers:
            print(f"- {paper}")

    # Prune evaluation papers using specialized topics
    def prune_papers(specialized_topics, evaluation_papers):
        """
        Use an LLM agent to filter evaluation papers based on specialized topics.
        """
        pruned_papers = {}

        def process_paper(topic, paper):
            input_text = f"""
            The project focuses on the following specialized topics: {', '.join(specialized_topics)}.
            Determine if the paper titled '{paper}' is directly relevant and truly essential to either one of these:
            1. general understanding of {topic}
            2. the project: {project_summary}.

            Respond with ONLY the word "yes" (nothing other than the word) if it is relevant or beneficial to understanding the topic in general.
            Otherwise respond with ONLY the word "no" (nothing other than the word).
            """
            try:
                response = gpt_agent.query("You are a helpful assistant.", input_text).strip().lower()
                print(f"Response for paper '{paper}': {response}")
                return paper if response == "yes" else None
            except Exception as e:
                print(f"Error processing paper '{paper}': {e}")
                return None

        with ThreadPoolExecutor() as executor:
            for topic, papers in evaluation_papers.items():
                futures = {executor.submit(process_paper, topic, paper): paper for paper in papers}
                pruned_papers[topic] = [future.result() for future in futures if future.result()]

        return pruned_papers

    pruned_selected_papers = prune_papers(specialized_concepts, selected_papers)

    pprint(pruned_selected_papers)
    print("\nPruned Selected Papers for Evaluation:")
    for topic, papers in pruned_selected_papers.items():
        print(f"\nTopic: {topic}")
        for paper in papers:
            print(f"- {paper}")

    def find_foundational_topics_and_resources(
        pruned_papers, existing_fundamental_concepts
    ):
        """
        Use an LLM agent to identify foundational topics required for the pruned list of papers
        and recommend resources for each topic in two passes.
        """
        foundational_topics = {}

        def process_paper_for_topics(paper):
            input_text = f"""
            The project involves the following paper: {paper}.
                Identify all foundational topics required to understand this paper.
                Include both the existing foundational topics: {', '.join(existing_fundamental_concepts)}
                and any additional foundational topics not listed. 
                Foundational concepts are foundational to the core concepts ({', '.join(core_concepts)}) and provide the necessary theoretical or technical background 
                to understand and work with the core concepts. Foundational topics should not include core concepts.
                They are more advanced than prerequisites but not as specific as core concepts. 
                Examples: Machine Learning, Deep Learning, Robotic Kinematics, Control Theory.
                Foundational topics should not be too basic either.
                Too basic: Linear Algebra, Calculus, Classical Mechanics.
                Respond in the following JSON format.
                Do NOT include tick marks or any other formatting. Just ONLY provide the JSON object:
                {{
                    "foundational_topics": [
                        {{
                            "topic": "<topic>"
                        }},
                        {{
                            "topic": "<topic>"
                        }}
                    ]
                }}
            """
            try:
                response = gpt_agent.query("You are a helpful assistant.", input_text)
                print(f"Response for foundational topics for paper '{paper}':", response)
                response_data = json.loads(response)
                return paper, response_data.get("foundational_topics", [])
            except Exception as e:
                print(f"Error generating foundational topics for paper '{paper}': {e}")
                return paper, []

        def process_paper_for_resources(paper, topics):
            input_text = f"""
            The following foundational topics have been identified for the paper '{paper}': {', '.join([t['topic'] for t in topics])}.
            For each topic, recommend a research paper, textbook, or resource that provides
            a comprehensive introduction to the topic. Respond in the following JSON format
            Do NOT include tick marks or any other formatting. Just ONLY provide the JSON object:
            {{
                "{paper}": [
                    {{
                        "topic": "<topic>",
                        "resource": "<resource title and author or link>"
                    }},
                    {{
                        "topic": "<topic>",
                        "resource": "<resource title and author or link>"
                    }}
                ]
            }}
            """
            try:
                response = gpt_agent.query("You are a helpful assistant.", input_text)
                print(f"Response for resources for paper '{paper}':", response)
                response_data = json.loads(response)
                return paper, response_data.get(paper, [])
            except Exception as e:
                print(f"Error generating resources for paper '{paper}': {e}")
                return paper, []

        # First pass: Generate foundational topics grouped by paper
        with ThreadPoolExecutor() as executor:
            future_to_paper = {
                executor.submit(process_paper_for_topics, paper): paper
                for topic, papers in pruned_papers.items()
                for paper in papers
            }
            for future in future_to_paper:
                paper, topics = future.result()
                foundational_topics[paper] = topics

        # Second pass: Attach resources to each foundational topic
        with ThreadPoolExecutor() as executor:
            future_to_paper = {
                executor.submit(process_paper_for_resources, paper, topics): paper
                for paper, topics in foundational_topics.items()
            }
            for future in future_to_paper:
                paper, resources = future.result()
                foundational_topics[paper] = resources

        return foundational_topics

    # Apply the agent to find foundational topics and resources
    final_foundational_topics = find_foundational_topics_and_resources(
        pruned_selected_papers, fundamental_concepts
    )

    # Output the final foundational topics and their resources
    print("\nFinal Foundational Topics and Recommended Resources:")
    for paper, topics in final_foundational_topics.items():
        print(f"\nPaper: {paper}")
        for topic in topics:
            print(f"- {topic['topic']}: {topic.get('resource', 'No resource available')}")

    # Build and visualize the tree graph
    G = build_tree_graph(
        project_title,
        core_concepts,
        pruned_selected_papers,
        final_foundational_topics,
    )
    visualize(G)


if __name__ == "__main__":
    main()
