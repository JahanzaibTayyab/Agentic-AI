from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import DuckDuckGoSearchRun
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.tools import BaseTool
from langchain.tools.base import ToolException
import streamlit as st
from PIL import Image
from typing import List, Optional, Any, Dict, Union
import tempfile
import os
import json

class ImageAnalysisTool(BaseTool):
    name: str = "image_analysis"
    description: str = "Analyzes images for design and UX patterns. Input should be a JSON string with 'query' and 'image_paths' keys."
    
    def _run(self, tool_input: str) -> str:
        """Run image analysis."""
        try:
            if isinstance(tool_input, str):
                parsed_input = json.loads(tool_input)
            else:
                parsed_input = tool_input
                
            image_paths = parsed_input.get("image_paths", [])
            query = parsed_input.get("query", "")
            
            if not image_paths:
                return "Error: No image paths provided in the tool input"
                
            # Here you would typically do the actual image analysis
            # For now, we'll return a placeholder response
            return f"Analysis complete for {len(image_paths)} images based on query: {query}"
            
        except json.JSONDecodeError:
            return "Error: Invalid JSON input format"
        except Exception as e:
            return f"Error during analysis: {str(e)}"

    def _arun(self, tool_input: str) -> str:
        """Run image analysis asynchronously."""
        raise NotImplementedError("Async not implemented")

def process_images(files) -> List[str]:
    """Process uploaded files and return list of temporary file paths."""
    processed_images: List[str] = []
    if not files:
        return processed_images
        
    for file in files:
        try:
            # Create a temporary file path
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"temp_{file.name}")
            
            # Save the uploaded file
            with open(temp_path, "wb") as f:
                f.write(file.getvalue())
            
            processed_images.append(temp_path)
            
        except Exception as e:
            st.error(f"Error processing image {file.name}: {str(e)}")
            continue
            
    return processed_images

def create_analysis_prompt(analysis_type: str, elements: List[str], context: str, image_paths: List[str]) -> str:
    """Create a properly formatted analysis prompt."""
    tool_input = {
        "query": f"""
        Analysis type: {analysis_type}
        Focus elements: {', '.join(elements)}
        Context: {context}
        """,
        "image_paths": image_paths
    }
    return json.dumps(tool_input)

def run_analysis(agent: AgentExecutor, analysis_type: str, elements: List[str], context: str, image_paths: List[str]) -> str:
    """Run analysis with proper input formatting."""
    try:
        # Create the formatted prompt
        prompt = f"""
        Please analyze these designs using the image_analysis tool.
        Analysis type: {analysis_type}
        Focus elements: {', '.join(elements)}
        Context: {context}
        
        You should:
        1. Use the image_analysis tool with the provided images
        2. Format your final answer as a clear analysis with markdown headers and bullet points
        """
        
        # Run the agent
        response = agent.invoke({
            "input": prompt,
            "tool_input": create_analysis_prompt(analysis_type, elements, context, image_paths)
        })
        
        return response.get("output", "No output generated")
    except Exception as e:
        return f"Error during analysis: {str(e)}"
    
def initialize_agents(api_key: str) -> tuple[AgentExecutor, AgentExecutor, AgentExecutor]:
    try:
        # Initialize the base LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.9,
        )
        
        # Create tools
        search_tool = DuckDuckGoSearchRun()
        image_tool = ImageAnalysisTool()
        
        # Vision Analysis Agent
        vision_template = """You are a visual analysis expert that:
        1. Identifies design elements, patterns, and visual hierarchy
        2. Analyzes color schemes, typography, and layouts
        3. Detects UI components and their relationships
        4. Evaluates visual consistency and branding
        
        Be specific and technical in your analysis.

        Tools available:
        {tools}
        
        Use the following format:
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        
        Question: {input}
        {agent_scratchpad}
        """
        
        vision_prompt = PromptTemplate.from_template(vision_template)
        vision_agent = create_react_agent(
            llm=llm,
            tools=[image_tool],
            prompt=vision_prompt
        )
        vision_executor = AgentExecutor(agent=vision_agent, tools=[image_tool])
        
        # UX Analysis Agent
        ux_template = """You are a UX analysis expert that:
        1. Evaluates user flows and interaction patterns
        2. Identifies usability issues and opportunities
        3. Suggests UX improvements based on best practices
        4. Analyzes accessibility and inclusive design
        
        Focus on user-centric insights and practical improvements.

        Tools available:
        {tools}
        
        Use the following format:
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        
        Question: {input}
        {agent_scratchpad}
        """
        
        ux_prompt = PromptTemplate.from_template(ux_template)
        ux_agent = create_react_agent(
            llm=llm,
            tools=[image_tool],
            prompt=ux_prompt
        )
        ux_executor = AgentExecutor(agent=ux_agent, tools=[image_tool])
        
        # Market Analysis Agent
        market_template = """You are a market research expert that:
        1. Identifies market trends and competitor patterns
        2. Analyzes similar products and features
        3. Suggests market positioning and opportunities
        4. Provides industry-specific insights
        
        Focus on actionable market intelligence.

        Tools available:
        {tools}
        
        Use the following format:
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        
        Question: {input}
        {agent_scratchpad}
        """
        
        market_prompt = PromptTemplate.from_template(market_template)
        market_agent = create_react_agent(
            llm=llm,
            tools=[search_tool, image_tool],
            prompt=market_prompt
        )
        market_executor = AgentExecutor(agent=market_agent, tools=[search_tool, image_tool])
        
        return vision_executor, ux_executor, market_executor
    except Exception as e:
        st.error(f"Error initializing agents: {str(e)}")
        return None, None, None
    
# Streamlit UI
st.title("Multimodal AI Design Agent Team")

# Sidebar for API key input
with st.sidebar:
    st.header("🔑 API Configuration")
    
    if "api_key_input" not in st.session_state:
        st.session_state.api_key_input = ""
    
    api_key = st.text_input(
        "Enter your Gemini API Key",
        value=st.session_state.api_key_input,
        type="password",
        help="Get your API key from Google AI Studio",
        key="api_key_widget"
    )
    
    if api_key != st.session_state.api_key_input:
        st.session_state.api_key_input = api_key
    
    if api_key:
        st.success("API Key provided! ✅")
    else:
        st.warning("Please enter your API key to proceed")
        st.markdown("""
        To get your API key:
        1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
        """)

if st.session_state.api_key_input:
    vision_agent, ux_agent, market_agent = initialize_agents(st.session_state.api_key_input)
    
    if all([vision_agent, ux_agent, market_agent]):
        # File Upload Section
        st.header("📤 Upload Content")
        col1, space, col2 = st.columns([1, 0.1, 1])
        
        with col1:
            design_files = st.file_uploader(
                "Upload UI/UX Designs",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                key="designs"
            )
            
            if design_files:
                for file in design_files:
                    image = Image.open(file)
                    st.image(image, caption=file.name, use_container_width=True)
        
        with col2:
            competitor_files = st.file_uploader(
                "Upload Competitor Designs (Optional)",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                key="competitors"
            )
            
            if competitor_files:
                for file in competitor_files:
                    image = Image.open(file)
                    st.image(image, caption=f"Competitor: {file.name}", use_container_width=True)
        
        # Analysis Configuration
        st.header("🎯 Analysis Configuration")
        
        analysis_types = st.multiselect(
            "Select Analysis Types",
            ["Visual Design", "User Experience", "Market Analysis"],
            default=["Visual Design"]
        )
        
        specific_elements = st.multiselect(
            "Focus Areas",
            ["Color Scheme", "Typography", "Layout", "Navigation", 
             "Interactions", "Accessibility", "Branding", "Market Fit"]
        )
        
        context = st.text_area(
            "Additional Context",
            placeholder="Describe your product, target audience, or specific concerns..."
        )
        
        # Analysis Process
        if st.button("🚀 Run Analysis", type="primary"):
            if design_files:
                try:
                    st.header("📊 Analysis Results")
                    
                    # Process all images once
                    design_images = process_images(design_files)
                    competitor_images = process_images(competitor_files) if competitor_files else []
                    all_images = design_images + competitor_images
                    
                    if not all_images:
                        st.warning("No images were successfully processed. Please check your uploads.")
                        st.stop()
                    
                    # Store the paths in session state to ensure they persist
                    st.session_state.image_paths = all_images
                    
                    # Run analyses based on selected types
                    if "Visual Design" in analysis_types:
                        with st.spinner("🎨 Analyzing visual design..."):
                            vision_result = run_analysis(
                                vision_agent,
                                "Visual Design",
                                specific_elements,
                                context,
                                st.session_state.image_paths
                            )
                            st.subheader("🎨 Visual Design Analysis")
                            st.markdown(vision_result)
                    
                    if "User Experience" in analysis_types:
                        with st.spinner("🔄 Analyzing user experience..."):
                            ux_result = run_analysis(
                                ux_agent,
                                "User Experience",
                                specific_elements,
                                context,
                                st.session_state.image_paths
                            )
                            st.subheader("🔄 UX Analysis")
                            st.markdown(ux_result)
                    
                    if "Market Analysis" in analysis_types:
                        with st.spinner("📊 Conducting market analysis..."):
                            market_result = run_analysis(
                                market_agent,
                                "Market Analysis",
                                specific_elements,
                                context,
                                st.session_state.image_paths
                            )
                            st.subheader("📊 Market Analysis")
                            st.markdown(market_result)
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
                    st.error("Please check your API key and try again.")
            else:
                st.warning("Please upload at least one design to analyze.")
    else:
        st.warning("Please upload at least one design to analyze.")
else:
    st.info("👈 Please enter your API key in the sidebar to get started")

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <h4>Tips for Best Results</h4>
    <p>
    • Upload clear, high-resolution images<br>
    • Include multiple views/screens for better context<br>
    • Add competitor designs for comparative analysis<br>
    • Provide specific context about your target audience
    </p>
</div>
""", unsafe_allow_html=True) 

# Footer
st.markdown("""
<div style='text-align: center'>
    <small>
    &copy; 2024 Multimodal AI Design Team. All rights reserved.
    </small>
</div>
""", unsafe_allow_html=True)