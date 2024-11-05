import wikipediaapi

def wiki_search():
    # Initialize Wikipedia API with user agent
    wiki = wikipediaapi.Wikipedia(
        'MyProject (your@email.com)',
        'en'  # Language
    )
    
    # Search for a page
    page = wiki.page('reinforcement learning')
    
    # Basic page information
    print(f"Page Title: {page.title}")
    print(f"\nPage Summary:\n{page.summary[:500]}...")
    print(f"\nPage URL: {page.fullurl}")
    
    # Get sections
    print("\nMain Sections:")
    for section in page.sections:
        print(f"- {section.title}")
    
    # Get references
    print("\nFirst 5 Categories:")
    for category in list(page.categories.keys())[:5]:
        print(f"- {category}")
    
    # Get language links
    print("\nAvailable in languages:")
    for lang in list(page.langlinks.keys())[:5]:
        print(f"- {lang}: {page.langlinks[lang].title}")

if __name__ == "__main__":
    wiki_search()