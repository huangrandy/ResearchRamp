import random

class EvalAgent:
    def __init__(self, seminal_paper_counts_by_topic):
        self.seminal_paper_counts_by_topic = seminal_paper_counts_by_topic

    def select_papers(self):
        """
        Select papers based on the following criteria:
        1. Include all papers with a count > 1.
        2. Include 30% of the remaining papers, prioritizing those with the highest counts.
        """
        selected_papers = {}

        for topic, paper_counts in self.seminal_paper_counts_by_topic.items():
            # Separate papers with count > 1 and count == 1
            high_count_papers = {paper: count for paper, count in paper_counts.items() if count > 1}
            low_count_papers = {paper: count for paper, count in paper_counts.items() if count == 1}

            # Add all high-count papers
            selected_papers[topic] = list(high_count_papers.keys())

            # Sort low-count papers by count (descending) and select 30% of them
            sorted_low_count_papers = sorted(low_count_papers.items(), key=lambda x: x[1], reverse=True)
            num_to_select = max(1, int(0.3 * len(sorted_low_count_papers)))  # Ensure at least one paper is selected
            selected_low_count_papers = [paper for paper, _ in sorted_low_count_papers[:num_to_select]]

            # Add selected low-count papers
            selected_papers[topic].extend(selected_low_count_papers)

        return selected_papers
