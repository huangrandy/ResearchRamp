# ResearchRamp 📚

ResearchRamp is an AI-powered academic paper analysis tool that helps researchers understand and explore relationships between research papers, concepts, and seminal works in their field. The system uses advanced AI techniques to analyze papers and create interactive visualizations of research networks.

## 🎯 Introduction

ResearchRamp addresses several key challenges in academic research:

1. **Information Overload**: With thousands of papers published daily, researchers struggle to keep up with relevant literature. ResearchRamp helps by:
   - Automatically extracting key concepts from papers
   - Identifying relationships between papers and concepts
   - Creating visual maps of research networks

2. **Research Discovery**: Finding relevant papers and understanding their relationships is time-consuming. ResearchRamp provides:
   - AI-powered paper analysis
   - Concept relationship mapping
   - Interactive visualization of research networks

3. **Impact Assessment**: Understanding a paper's influence and connections is crucial. ResearchRamp offers:
   - Seminal work detection
   - Citation pattern analysis
   - Research evolution tracking

## ⚙️ Prerequisites

Before installing ResearchRamp, ensure you have the following:

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 1GB free disk space
- Internet connection for API access

### Required Software
1. **Python Environment**
   - Python 3.8+
   - pip (Python package manager)
   - virtualenv or conda (recommended)

2. **Development Tools**
   - Git
   - A code editor (VS Code recommended)
   - Terminal/Command Prompt

3. **API Access**
   - OpenAI API key
   - Valid API credentials

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ResearchRamp.git
cd ResearchRamp
```

### 2. Set Up Python Environment
```bash
# Using virtualenv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n researchramp python=3.8
conda activate researchramp
```

### 3. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install additional system dependencies (if needed)
# On Ubuntu/Debian:
sudo apt-get install python3-dev
# On macOS:
brew install python3
```

### 4. Configure Environment
Create a `.env` file in the project root:
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here

# Application Settings
FLASK_ENV=development
DEBUG=True

# Optional: Database Configuration
DATABASE_URL=sqlite:///researchramp.db
```

### 5. Initialize the System
```bash
# Initialize the database
python src/utils/db_init.py

# Run initial setup
python src/setup.py
```

### 6. Verify Installation
```bash
# Run tests
python -m pytest tests/

# Start the application
python src/main_workflow.py
```

## 🏃‍♂️ Running the Application

### Starting the Server

1. **Activate the Environment**
```bash
# If using virtualenv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# If using conda
conda activate researchramp
```

2. **Start the Application**
```bash
python src/main_workflow.py
```

The application will start and be available at `http://localhost:5000` by default.

### Using the Application

1. **Paper Analysis**
   - Navigate to the main interface
   - Input a paper ID or upload a PDF
   - Click "Analyze" to start the process
   - View the extracted concepts and relationships

2. **Network Visualization**
   - The network graph will automatically load
   - Use mouse/touch gestures to:
     - Zoom: Scroll or pinch
     - Pan: Click and drag
     - Select: Click on nodes
   - Hover over nodes for quick information
   - Click nodes for detailed view

3. **Seminal Work Detection**
   - Select "Seminal Analysis" from the menu
   - Choose a research area or paper
   - View the analysis results
   - Explore related papers

### Common Operations

1. **Adding New Papers**
```bash
# Using the command line
python src/utils/paper_utils.py add --paper_id "your_paper_id"

# Or through the web interface
# Navigate to "Add Paper" section
```

2. **Updating the Network**
```bash
# Refresh the visualization
python src/utils/graph_utils.py update

# Or use the "Refresh" button in the interface
```

3. **Exporting Results**
   - Use the "Export" button in the interface
   - Choose format (JSON, CSV, or PNG)
   - Select the data to export

### Troubleshooting

1. **Server Issues**
   - Check if the port 5000 is available
   - Verify environment variables are set
   - Check the logs in `logs/app.log`

2. **Visualization Problems**
   - Clear browser cache
   - Check browser console for errors
   - Verify network connectivity

3. **API Errors**
   - Verify OpenAI API key is valid
   - Check API rate limits
   - Review error messages in logs

### Stopping the Application

1. **Graceful Shutdown**
   - Press `Ctrl+C` in the terminal
   - Wait for the shutdown message
   - Verify all processes are stopped

2. **Force Stop (if needed)**
```bash
# Find the process
ps aux | grep main_workflow.py

# Stop the process
kill -9 <process_id>
```

## 🔮 Next Steps

### 1. Enhanced AI Capabilities
- **Fine-tuned Models**: Train specialized models for different research domains
- **Multi-model Ensemble**: Combine multiple AI models for better accuracy
- **Custom Training**: Add support for training on user-specific research data

### 2. Feature Enhancements
- **Real-time Collaboration**: Add support for multiple users working simultaneously
- **Advanced Search**: Implement semantic search across papers and concepts
- **Automated Literature Reviews**: Generate comprehensive literature reviews
- **Citation Network Analysis**: Enhanced analysis of paper citations and impact

### 3. User Experience Improvements
- **Mobile Support**: Optimize interface for mobile devices
- **Customizable Dashboards**: Allow users to create personalized views
- **Export Options**: Add more export formats and visualization styles
- **Batch Processing**: Support for analyzing multiple papers simultaneously

### 4. Technical Improvements
- **Performance Optimization**: Improve processing speed for large networks
- **Scalability**: Enhance system to handle larger datasets
- **API Expansion**: Add more endpoints for external integration
- **Caching System**: Implement intelligent caching for faster responses

### 5. Integration Capabilities
- **Academic Databases**: Add support for more paper repositories
- **Reference Managers**: Integration with tools like Zotero and Mendeley
- **Collaboration Tools**: Connect with academic collaboration platforms
- **Publication Systems**: Direct integration with journal submission systems

### 6. Documentation and Support
- **API Documentation**: Comprehensive API documentation
- **User Guides**: Detailed guides for different user roles
- **Video Tutorials**: Step-by-step video guides
- **Community Forum**: Platform for user discussions and support

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the AI capabilities
- vis-network for the visualization library
- The academic community for inspiration and research papers
