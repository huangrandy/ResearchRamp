import json
import os
from agents.general_agent import Agent


class ConceptExtractionAgent:
    def __init__(self, gpt_agent: Agent, queries_folder="queries"):
        self.gpt_agent = gpt_agent
        self.queries_folder = queries_folder

    def extract_concepts(self, filename: str):
        """
        Extract concepts from a project description using GPT API.
        """
        file_path = os.path.join(self.queries_folder, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        with open(file_path, "r") as file:
            project_data = json.load(file)

        # Extract the project description
        description = project_data.get("description", "")
        if not description:
            raise ValueError("Project description is missing in the JSON file.")

        # Query GPT to infer concepts
        concepts = self._query_gpt_for_concepts(description)
        return concepts

    def _query_gpt_for_concepts(self, description: str):
        """
        Query GPT to infer concepts from the project description.
        """
        input_text = f"""
        Analyze the following project description and extract concepts into four categories:
        - Prerequisites: Static knowledge/skills the user must already possess.
        - Fundamental: Project-specific prerequisites needed to engage with core concepts.
        - Core: Central focus areas of the project. 
        - Specialized: Applied implementations of core concepts.

        Project Description:
        {description}

        Provide the output in the following JSON format.
        Do NOT include tick marks or any other formatting. Just ONLY provide the JSON object:
        {{
            "prerequisites": ["<list of concepts>"],
            "fundamental_concepts": ["<list of concepts>"],
            "core_concepts": ["<list of concepts>"],
            "specialized_concepts": ["<list of concepts>"]
        }}
        """
        try:
            response = self.gpt_agent.query("You are a helpful assistant.", input_text)
            print("GPT response:", response)  # Debugging line
            return json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(
                "Failed to parse GPT response. Ensure the response is in the correct JSON format."
            )
