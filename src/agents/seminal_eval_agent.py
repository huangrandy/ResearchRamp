class SeminalEvalAgent:
    def __init__(self, seminal_paper_counts_by_topic, gpt_agent):
        self.seminal_paper_counts_by_topic = seminal_paper_counts_by_topic
        self.gpt_agent = gpt_agent

    def select_papers(self):
        """
        Select papers based on the following criteria:
        1. Include all papers with a count > 1.
        2. Use the agent to determine 30% of the remaining papers, prioritizing those with the highest counts.
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

            # Use the agent to determine the 30% most relevant of the remaining papers in one query
            if low_count_papers:
                input_text = f"""
                    Assess the relevance of the following papers to the topic '{topic}' in the context of this project.
                    Provide a relevance score between 0 and 1 for each paper, where 1 is highly relevant and 0 is not relevant at all.
                    Papers: {', '.join(low_count_papers.keys())}
                """
                
                try:
                    relevance_scores = self.gpt_agent.query("You are a helpful assistant.", input_text).strip()
                    # Parse the response into a dictionary of paper -> relevance score
                    low_count_paper_relevance = {
                    paper: float(score) for paper, score in 
                    (item.split(':') for item in relevance_scores.split('\n') if ':' in item)
                    }
                except Exception as e:
                    print(f"Error assessing relevance for topic '{topic}': {e}")
                    low_count_paper_relevance = {paper: 0 for paper in low_count_papers.keys()}  # Default to 0

            # Sort low-count papers by relevance score (descending) and select 30% of them
            sorted_low_count_papers = sorted(
                low_count_paper_relevance.items(), key=lambda x: x[1], reverse=True
            )
            num_to_select = max(
                1, int(0.3 * len(sorted_low_count_papers))
            )  # Ensure at least one paper is selected
            selected_low_count_papers = [
                paper for paper, _ in sorted_low_count_papers[:num_to_select]
            ]

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
