import json
import os
from agents.general_agent import Agent

# Inline implementation of ConceptExtractionAgent for debugging
class ConceptExtractionAgent:
    def __init__(self, gpt_agent, queries_folder="queries"):
        self.gpt_agent = gpt_agent
        self.queries_folder = queries_folder

    def extract_concepts(self, filename):
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
        return self._query_gpt_for_concepts(description)

    def _query_gpt_for_concepts(self, description):
        """
        Query GPT to infer concepts from the project description.
        """
        input_text = f"""
        Analyze the following project description and extract the following information:

        - Project Title: A concise title summarizing the project.
        - Project Summary: A brief summary of the project in 2-3 sentences.
        - Prerequisites: These are the static knowledge, skills, or tools that the user must already possess before engaging with the project. 
          They are typically foundational and do not require further explanation within the context of the project. 
          Examples include basic programming skills, familiarity with Python, linear algebra, or basic calculus. 
          Avoid listing concepts that are introduced or developed as part of the project itself.
        - Fundamental Concepts: These are foundational to the core concepts and provide the necessary theoretical or technical background 
          to understand and work with the core concepts. They are more advanced than prerequisites but not as specific as core concepts. 
          Examples: Machine Learning, Deep Learning, Robotic Kinematics, Control Theory.
        - Core Concepts: These are the central focus areas of the project and represent the main topics or themes the project is addressing. 
          They are typically the tags or keywords associated with the project. 
          Examples: Reinforcement Learning (RL), Computer Vision, Robotics.
        - Specialized Concepts: These are specific applications or implementations of the core concepts within the context of the project. 
          They are highly specific and often represent advanced or applied topics. 
          Examples: RL for Grasping Strategies, Sim-to-Real Transfer, Affordance-Based Manipulation.

        Project Description:
        {description}

        Provide the output in the following JSON format.
        Do NOT include tick marks or any other formatting. Just ONLY provide the JSON object:
        {{
            "project_title": "<project title>",
            "project_summary": "<project summary>",
            "prerequisites": ["<list of concepts>"],
            "fundamental_concepts": ["<list of concepts>"],
            "core_concepts": ["<list of concepts>"],
            "specialized_concepts": ["<list of concepts>"]
        }}
        """
        try:
            response = self.gpt_agent.query("You are a helpful assistant.", input_text)
            print("Concepts and Metadata:\n", response)  # Debugging line
            return json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(
                "Failed to parse GPT response. Ensure the response is in the correct JSON format."
            )
