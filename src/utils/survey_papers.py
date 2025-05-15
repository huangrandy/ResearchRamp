from concurrent.futures import ThreadPoolExecutor
import json


def query_survey_papers(core_concepts, gpt_agent):
    """
    Query for survey papers for each core concept.
    """
    survey_papers = {}

    def find_survey_papers(concept):
        input_text = f"""
        Provide 6 survey papers on the topic '{concept}' in the following JSON format.
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

    return survey_papers
