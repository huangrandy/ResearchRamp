from concurrent.futures import ThreadPoolExecutor
import json


def find_foundational_topics_and_resources(
    pruned_papers, existing_fundamental_concepts, gpt_agent, core_concepts
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
