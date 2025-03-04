## 🏠 AI Real Estate Agent - Powered by Firecrawl's Extract Endpoint

The AI Real Estate Agent automates property search and market analysis using Firecrawl's Extract endpoint and Agno AI Agent's insights. It helps users find properties matching their criteria while providing detailed location trends and investment recommendations. This agent streamlines the property search process by combining data from multiple real estate websites and offering intelligent analysis.

### Features

- **Smart Property Search**: Uses Firecrawl's Extract endpoint to find properties across multiple real estate websites
- **Location Analysis**: Provides detailed price trends and investment insights for different localities
- **AI-Powered Recommendations**: Uses Gemini models to analyze properties and provide structured recommendations
- **User-Friendly Interface**: Clean Streamlit UI for easy property search and results viewing
- **Customizable Search**: Filter by city, property type, category, and budget

## Live Demo

Experience the application: [AI Design Agent Team](https://ai-real-estate-agent.streamlit.app/)

## Application Screenshot

![Application Screenshot](./image.png)

### How to Get Started

### 1. **Setup Environment**

```bash
# Clone the repository
# Create and activate virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Set up your API keys**:

   - Get your Firecrawl API key from [Firecrawl's website](https://www.firecrawl.dev/app/api-keys)
   - Get your Gemini API key from [AI Studio website](https://aistudio.google.com/)

3. **Run the application**:
   ```bash
   streamlit run ai_real_estate_agent.py
   ```

### Using the Agent

1. **Enter API Keys**:

   - Input your Firecrawl and Gemini API keys in the sidebar
   - Keys are securely stored in the session state

2. **Set Search Criteria**:

   - Enter the city name
   - Select property category (Residential/Commercial)
   - Choose property type (Flat/Individual House)
   - Set maximum budget in Crores

3. **View Results**:
   - Property recommendations with detailed analysis
   - Location trends with investment insights
   - Expandable sections for easy reading

### Features in Detail

- **Property Finding**:

  - Searches across multiple real estate websites
  - Returns 3-6 properties matching criteria
  - Provides detailed property information and analysis

- **Location Analysis**:
  - Price trends for different localities
  - Rental yield analysis
  - Investment potential assessment
  - Top performing areas identification
