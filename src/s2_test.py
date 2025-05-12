from semanticscholar import SemanticScholar
from typing import List, Dict
import time
import os
import json
from datetime import datetime

def search_for_survey_papers(
    topics: List[str], year_range: str, max_papers_per_topic: int = 3
) -> Dict[str, List[Dict]]:
    """
    Search for survey papers on Semantic Scholar for each topic.

    Args:
        topics: List of research topics to search
        year_range: String in format "YYYY-YYYY" for publication years
        max_papers_per_topic: Maximum number of survey papers to retrieve per topic

    Returns:
        Dictionary mapping topics to lists of survey papers
    """
    s2 = SemanticScholar(timeout=30)  # Set timeout to avoid hanging
    fields = [
        "title",
        "url",
        "year",
        "citationCount",
        "isOpenAccess",
        "authors",
        "abstract",
    ]
    survey_keywords = [
        "survey",
        "review",
        "overview",
        "systematic analysis",
        "meta-analysis",
        "state of the art",
    ]
    results = {}

    for topic in [topics[0]]:
        print(f"Searching for survey papers on: {topic}")
        results[topic] = []

        try:
            # First attempt: search with survey keyword in query
            survey_query = f"{topic} survey"
            papers = s2.search_paper(
                survey_query,
                fields=fields,
                year=year_range,
                limit=15,  # Get more than needed to filter
            )

            # Filter for survey papers by looking at titles
            survey_papers = []
            for paper in papers:
                if any(keyword in paper.title.lower() for keyword in survey_keywords):
                    author_name = paper.authors[0].name if paper.authors else "Unknown"
                    paper_data = {
                        "title": paper.title,
                        "first_author": author_name,
                        "year": paper.year,
                        "citation_count": paper.citationCount,
                        "url": paper.url,
                        "is_open_access": paper.isOpenAccess,
                        "abstract": (
                            paper.abstract[:200] + "..."
                            if paper.abstract
                            else "No abstract available"
                        ),
                    }
                    survey_papers.append(paper_data)

                    if len(survey_papers) >= max_papers_per_topic:
                        break

            # If we didn't find enough survey papers, try a more general search
            if len(survey_papers) < max_papers_per_topic:
                general_papers = s2.search_paper(
                    topic, fields=fields, year=year_range, limit=15
                )

                for paper in general_papers:
                    # Skip papers we've already found
                    if any(p["title"] == paper.title for p in survey_papers):
                        continue

                    # Check if it might be a survey based on title
                    if any(
                        keyword in paper.title.lower() for keyword in survey_keywords
                    ):
                        author_name = (
                            paper.authors[0].name if paper.authors else "Unknown"
                        )
                        paper_data = {
                            "title": paper.title,
                            "first_author": author_name,
                            "year": paper.year,
                            "citation_count": paper.citationCount,
                            "url": paper.url,
                            "is_open_access": paper.isOpenAccess,
                            "abstract": (
                                paper.abstract[:200] + "..."
                                if paper.abstract
                                else "No abstract available"
                            ),
                        }
                        survey_papers.append(paper_data)

                    if len(survey_papers) >= max_papers_per_topic:
                        break

            # Store the results
            results[topic] = survey_papers
            print(f"  Found {len(survey_papers)} survey papers")

            # Add a delay to avoid rate limiting
            time.sleep(1)

        except Exception as e:
            print(f"Error searching for topic '{topic}': {str(e)}")

    return results


def format_results_for_output(survey_results: Dict[str, List[Dict]]) -> str:
    """Format the survey results into a readable string for output."""
    output = []
    
    for topic, papers in survey_results.items():
        output.append(f"== SURVEY PAPERS FOR: {topic} ==")
        if not papers:
            output.append("  No survey papers found")
            continue

        for i, paper in enumerate(papers, 1):
            output.append(f"\n{i}. {paper['title']}")
            output.append(f"   Author: {paper['first_author']} ({paper['year']})")
            output.append(f"   Citations: {paper['citation_count']}")
            output.append(f"   URL: {paper['url']}")
            output.append(f"   Open Access: {'Yes' if paper['is_open_access'] else 'No'}")
            output.append(f"   Abstract: {paper['abstract']}")
            output.append("")
    
    return "\n".join(output)

def save_results_to_file(survey_results: Dict[str, List[Dict]], output_dir: str, format: str = 'txt') -> str:
    """
    Save the survey results to a file in the specified output directory.
    
    Args:
        survey_results: Dictionary of survey results
        output_dir: Directory to save the output file
        format: Output format ('txt' or 'json')
        
    Returns:
        Path to the output file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format.lower() == 'json':
        filename = f"survey_papers_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(survey_results, f, indent=2)
    else:
        filename = f"survey_papers_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(format_results_for_output(survey_results))
    
    return filepath

topics = [
    "Reinforcement learning in robotics",
    "Adaptive object manipulation",
    "Computer vision for robotic grasping",
    "Self-improving robotic systems",
]

year_range = "2020-2025"

print("Starting survey paper search...")
survey_results = search_for_survey_papers(topics, year_range)

# Print the results in a readable format
def display_and_save_results(survey_results: Dict[str, List[Dict]], output_dir: str) -> None:
    """Display the survey results and save them to files."""
    for topic, papers in survey_results.items():
        print(f"\n== SURVEY PAPERS FOR: {topic} ==")
        if not papers:
            print("  No survey papers found")
            continue

        for i, paper in enumerate(papers, 1):
            print(f"\n{i}. {paper['title']}")
            print(f"   Author: {paper['first_author']} ({paper['year']})")
            print(f"   Citations: {paper['citation_count']}")
            print(f"   URL: {paper['url']}")
            print(f"   Open Access: {'Yes' if paper['is_open_access'] else 'No'}")
            print(f"   Abstract: {paper['abstract']}")

    # Save the results to a file in the specified output directory
    output_filepath = save_results_to_file(survey_results, output_dir)
    print(f"\nResults saved to: {output_filepath}")

    # Also save as JSON for programmatic access
    json_filepath = save_results_to_file(survey_results, output_dir, format='json')
    print(f"Results saved as JSON to: {json_filepath}")

output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")

# Display and save the results
display_and_save_results(survey_results, output_dir)
