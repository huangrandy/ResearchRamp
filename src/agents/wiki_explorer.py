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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class WikiExplorationState(BaseModel):
    """State for Wikipedia exploration process"""
    topic: str
    key_concepts: Dict[str, List[str]] = Field(default_factory=dict)
    references: Dict[str, List[str]] = Field(default_factory=dict)
    researchers: List[str] = Field(default_factory=list)
    subtopics: List[str] = Field(default_factory=list)

class WikiExplorationAgent:
    def __init__(self):
        self.wiki_api = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='research_graph_builder/1.0'
        )
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv('OPENAI_API_KEY')
        )

    def explore_main_topic(self, topic: str) -> Dict[str, Any]:
        """Explores main topic Wikipedia page"""
        logger.info(f"Exploring main topic: {topic}")
        
        # Get Wikipedia page
        page = self.wiki_api.page(topic)
        if not page.exists():
            raise ValueError(f"Wikipedia page for '{topic}' does not exist")

        # Create prompt for GPT-4
        prompt = f"""
        Analyze this Wikipedia content for {topic}:
        {page.text[:4000]}
        
        Extract and return a JSON object with the following structure:
        {{
            "key_concepts": ["concept1", "concept2", ...],
            "subtopics": ["subtopic1", "subtopic2", ...],
            "researchers": ["researcher1", "researcher2", ...],
            "references": ["reference1", "reference2", ..."],
            "summary": "brief overview of the topic"
        }}
        
        Return only the JSON object, with no extra text, markdown syntax, or formatting.
        Ensure:
        1. Key concepts are fundamental ideas necessary to understand this topic
        2. Subtopics are major areas within this field
        3. Researchers include significant contributors to the field
        4. References are important papers or books
        5. Summary is a concise explanation of the topic
        """
        
        try:
            # Get GPT-4 analysis
            response = self.llm.invoke([HumanMessage(content=prompt)])
    
            analysis = json.loads(response.content)
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            filename = f"{output_dir}/{topic.replace(' ', '_')}_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            logger.info(f"Analysis completed and saved to {filename}")
            logger.info(f"Found {len(analysis['key_concepts'])} key concepts")
            
            return {
                "status": "success",
                "data": analysis,
                "output_file": filename
            }
            
        except Exception as e:
            logger.error(f"Error in main topic exploration: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

def run_exploration(topic: str) -> None:
    """Runs the Wikipedia exploration for a single topic"""
    agent = WikiExplorationAgent()
    
    try:
        results = agent.explore_main_topic(topic)
        
        if results["status"] == "success":
            print("\nExploration Results:")
            print(f"Key Concepts: {len(results['data']['key_concepts'])}")
            print(f"Subtopics: {len(results['data']['subtopics'])}")
            print(f"Researchers: {len(results['data']['researchers'])}")
            print(f"References: {len(results['data']['references'])}")
            print(f"\nSummary: {results['data']['summary']}")
            print(f"\nResults saved to: {results['output_file']}")
        else:
            print(f"Error: {results['error']}")
            
    except Exception as e:
        print(f"Error running exploration: {str(e)}")

if __name__ == "__main__":
    # Example usage
    topic = "Reinforcement Learning"  # You can change this to any topic
    run_exploration(topic)