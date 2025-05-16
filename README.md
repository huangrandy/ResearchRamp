# ResearchRamp 📚

ResearchRamp is an AI-powered academic paper analysis tool that helps researchers understand and explore relationships between research papers, concepts, and seminal works in their field. The system uses advanced AI techniques to analyze papers and create interactive visualizations of research networks.

## 🎯 Introduction

ResearchRamp addresses several key challenges in academic research:

1. **Information Overload**: With thousands of papers published daily, researchers struggle to keep up with relevant literature. ResearchRamp helps by:
   - Automatically extracting key concepts from papers
   - Identifying relationships between papers and concepts
   - Creating visual maps of research networks

2. **Research Discovery**: Finding relevant papers and understanding their relationships is time-consuming. ResearchRamp provides:
   - Concept relationship mapping
   - Interactive visualization of research networks

## ⚙️ Prerequisites
- Python 3.12.7 or higher
- OpenAI API key access

## 🚀 Running the application

### 1. Clone the Repository
```bash
git clone https://github.com/<yourusername>/ResearchRamp.git
cd ResearchRamp
```

### 2. Set Up Python Environment
```bash
# Using virtualenv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n researchramp python=3.12.7
conda activate researchramp
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_api_key_here
```


## 🏃‍♂️ Running the Application

**Start the Application**

In the main project directory, run the following command to start the application:
```bash
python src/main_workflow.py <project_name>
```
Replace `<project_name>` with the desired project file name, which are located in /queries. 

Currently the only projects that exist are `db`, `hci`, `network`, `nlp`, `robotics`, but you may create your own project JSON file, assuming the same format as the existing files.

After running the application, the knowledge graph HTML file (located in /src) can be viewed in the browser for visualization.
