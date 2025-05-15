import json

class SeminalEvalAgent:
    def __init__(self, seminal_paper_counts_by_topic, gpt_agent, project_summary):
        self.seminal_paper_counts_by_topic = seminal_paper_counts_by_topic
        self.gpt_agent = gpt_agent
        self.project_summary = project_summary

    def select_papers(self):
        """
        Select papers based on the following criteria:
        1. Include all papers with a count > 1.
        2. Use the agent to determine the top 6 most relevant papers from the remaining ones, preserving their ranking.
        """
        selected_papers = {}

        for topic, paper_counts in self.seminal_paper_counts_by_topic.items():
            # Separate papers with count > 1 and count == 1
            high_count_papers = {
                paper: count for paper, count in paper_counts.items() if count > 1
            }
            low_count_papers = {
                paper: count for paper, count in paper_counts.items() if count == 1
            }

            # Add all high-count papers
            selected_papers[topic] = list(high_count_papers.keys())
            print(f"Topic '{topic}': High-count papers selected: {selected_papers[topic]}")

            # Use the agent to determine the top 6 most relevant papers from the remaining ones
            if low_count_papers:
                input_text = f"""
                The project summary is as follows: {self.project_summary}.
                Assess the relevance of the following papers to the topic '{topic}' in the context of this project.
                Rank the papers by relevance and provide the top 6 most relevant papers in a JSON array format.
                Papers: {', '.join(low_count_papers.keys())}
                Respond in the following format:
                {{
                    "top_papers": ["<paper title>", "<paper title>", ...]
                }}
                """
                try:
                    response = self.gpt_agent.query("You are a helpful assistant.", input_text).strip()
                    response_data = json.loads(response)
                    selected_low_count_papers = response_data.get("top_papers", [])
                except Exception as e:
                    print(f"Error assessing relevance for topic '{topic}': {e}")
                    selected_low_count_papers = []

                # Add selected low-count papers
                selected_papers[topic].extend(selected_low_count_papers)

            print(f"Topic '{topic}': Final selected papers: {selected_papers[topic]}")

        return selected_papers

    def explain_relevance(self, selected_papers):
        """
        Use agent to explain why each selected paper is relevant to the project.
        """
        explanations = {}

        for topic, papers in selected_papers.items():
            explanations[topic] = {}
            for paper in papers:
                input_text = f"""
                Explain why the paper titled '{paper}' is relevant to the topic '{topic}' in the context of this project.
                Provide a concise explanation of its significance and how it contributes to the understanding or advancement of the topic.
                """
                try:
                    response = self.gpt_agent.query("You are a helpful assistant.", input_text)
                    explanations[topic][paper] = response.strip()
                except Exception as e:
                    explanations[topic][paper] = f"Error generating explanation: {e}"

        return explanations
