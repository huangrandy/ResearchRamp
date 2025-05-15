from concurrent.futures import ThreadPoolExecutor


def prune_papers(specialized_topics, evaluation_papers, gpt_agent, project_summary):
    """
    Prune evaluation papers using specialized topics.
    """
    pruned_papers = {}

    def process_paper(topic, paper):
        input_text = f"""
        The project focuses on the following specialized topics: {', '.join(specialized_topics)}.
        Determine if the paper titled '{paper}' is directly relevant and truly essential to either one of these:
        1. general understanding of {topic}
        2. the project: {project_summary}.

        Respond with ONLY the word "yes" (nothing other than the word) if it is relevant or beneficial to understanding the topic in general.
        Otherwise respond with ONLY the word "no" (nothing other than the word).
        """
        try:
            response = gpt_agent.query("You are a helpful assistant.", input_text).strip().lower()
            print(f"Response for paper '{paper}': {response}")
            return paper if response == "yes" else None
        except Exception as e:
            print(f"Error processing paper '{paper}': {e}")
            return None

    with ThreadPoolExecutor() as executor:
        for topic, papers in evaluation_papers.items():
            futures = {executor.submit(process_paper, topic, paper): paper for paper in papers}
            pruned_papers[topic] = [future.result() for future in futures if future.result()]

    return pruned_papers
