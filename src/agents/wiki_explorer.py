import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import wikipediaapi
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class ProjectQuery(BaseModel):
    """Query structure for project-based exploration"""

    project_title: str  # Renamed from 'topic' to 'project_title'
    project_description: str


class WikiExplorationState(BaseModel):
    """State for Wikipedia exploration process"""

    project_title: str
    project_description: str
    key_concepts: Dict[str, List[str]] = Field(default_factory=dict)
    references: Dict[str, List[str]] = Field(default_factory=dict)
    researchers: List[str] = Field(default_factory=list)
    subtopics: List[str] = Field(default_factory=list)


class WikiExplorationAgent:
    def __init__(self):
        self.wiki_api = wikipediaapi.Wikipedia(
            language="en",
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent="research_graph_builder/1.0",
        )
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY")
        )

    def extract_main_topics(self, project_title: str, project_description: str) -> List[str]:
        """Use LLM to identify main topics based on project title and description."""
        prompt = f"""
        Based on the following project title and description, identify the main focused topics that can be researchable categories related to the project, along with associated subtopics for each that are relevant to this project:

        Project Title: {project_title}  
        Project Description: {project_description}  

        Return the focused topics and their subtopics as a JSON array object. 
        Each main topic should be a high-level area of study relevant to the project, and please ensure that related concepts are grouped appropriately to minimize overlap and allow for depth of research. 
        Main topics should be researchable by themselves so that they are valuable as background knowledge for this project. 
        Do not include any code block markers, backticks, or formatting. Return only the raw JSON array.
        """

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            topics = json.loads(response.content)
            return topics
        except Exception as e:
            logger.error(f"Error extracting main topics: {str(e)}")
            raise

    def explore_main_topics(self, query: ProjectQuery) -> Dict[str, Any]:
        """Explore each main topic Wikipedia page with project context"""
        # Extract main topics from the title and description
        try:
            topics = self.extract_main_topics(query.project_title, query.project_description)
            logger.info(f"Extracted main topics: {topics}")
        except Exception as e:
            logger.error(f"Failed to extract main topics: {str(e)}")
            topics = [query.project_title]  # Fallback to the project title as the only topic

        # Initialize results structure
        exploration_results = {
            "project_analysis": {},
            "topics": {}
        }

        # Explore each topic and fetch Wikipedia content
        for topic in topics:
            logger.info(f"Exploring topic: {topic}")
            page = self.wiki_api.page(topic)
            if not page.exists():
                logger.warning(f"Wikipedia page for '{topic}' does not exist")
                continue

            # Create context-aware prompt
            prompt = f"""
            Analyze this Wikipedia content for {topic} in the context of the following project:
            
            Project Description:
            {query.project_description}

            Wikipedia Content:
            {page.text[:4000]}
            
            Project Requirements:
            {json.dumps(requirements, indent=2) if requirements else "Not available"}
            
            
            Extract and return a JSON object with:
            {{
                "key_concepts": {{
                    "concept": "description",
                    "relevance_to_project": "explanation"
                }},
                "subtopics": {{
                    "subtopic": "relevance_score_0_to_10"
                }},
                "researchers": ["researcher1", "researcher2", ...],
                "references": {{
                    "reference": "relevance_to_project"
                }},
                "learning_path": {{
                    "phase": ["topic1", "topic2", ...]
                }},
                "summary": "project-focused overview of the topic"
            }}
            
            Return only the JSON object, with no extra text, markdown syntax, or formatting.
            Focus on aspects most relevant to the project goals.
            """

            try:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                analysis = json.loads(response.content)
                exploration_results["topics"][topic] = analysis
            except Exception as e:
                logger.error(f"Error in main topic exploration for '{topic}': {str(e)}")
                continue

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filename = f"{output_dir}/{query.project_title.replace(' ', '_')}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(exploration_results, f, indent=2)

        logger.info(f"Exploration completed and saved to {filename}")

        return {"status": "success", "data": exploration_results, "output_file": filename}


def run_exploration(query: Dict[str, str]) -> None:
    """Runs the Wikipedia exploration for a project query"""
    try:
        # Convert dict to ProjectQuery model
        project_query = ProjectQuery(**query)

        agent = WikiExplorationAgent()
        results = agent.explore_main_topics(project_query)

        if results["status"] == "success":
            print("\nExploration Results:")
            print("\nProject Analysis:")
            print(
                f"Core Technical Areas: {len(results['data']['project_analysis'].get('core_technical_areas', []))}"
            )
            print(
                f"Required Background: {len(results['data']['project_analysis'].get('required_background', []))}"
            )

            print("\nTopic Analysis:")
            for topic, analysis in results["data"]["topics"].items():
                print(f"\nTopic: {topic}")
                print(f"Key Concepts: {len(analysis['key_concepts'])}")
                print(f"Subtopics: {len(analysis['subtopics'])}")
                print(f"References: {len(analysis['references'])}")

            print(f"\nResults saved to: {results['output_file']}")
        else:
            print(f"Error: {results['error']}")

    except Exception as e:
        print(f"Error running exploration: {str(e)}")


if __name__ == "__main__":
    # Example usage
    test_query = {
        "project_title": "Learning to Grasp: A Self-Improving Robotic System for Adaptive Object Manipulation",
        "project_description": """
        Developing a robotic system that can learn to manipulate objects in unstructured environments. 
        The system will use reinforcement learning to acquire manipulation skills through trial and error, 
        with the goal of generalizing to novel objects and situations. The project involves developing 
        both the learning algorithms and the robotic control infrastructure.
        
        The system will need to:
        1. Process visual input to identify objects
        2. Plan appropriate grasping strategies
        3. Execute manipulation tasks
        4. Learn from successful and failed attempts
        
        The initial implementation will focus on pick-and-place tasks with common household objects,
        with the goal of expanding to more complex manipulation sequences.
        """,
    }

    run_exploration(test_query)