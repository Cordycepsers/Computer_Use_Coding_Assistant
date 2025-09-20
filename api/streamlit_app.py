import streamlit as st
import requests
import json
import os
import time

st.set_page_config(
    page_title="Computer Use Coding Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main { padding-top: 2rem; }
    .stButton>button {
        background-color: #0084ff;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #0066cc;
        transform: translateY(-2px);
    }
    .success-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Computer Use Coding Assistant")
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        help="Enter your Anthropic API key"
    )
    
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key
        st.success("✅ API Key configured")
    else:
        st.warning("⚠️ Please enter your API key")
    
    st.markdown("---")
    st.header("📊 System Status")
    
    # Check API status
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            st.success("🟢 API Online")
        else:
            st.error("🔴 API Offline")
    except:
        st.error("🔴 API Unreachable")
    
    st.markdown("---")
    st.header("🔗 Quick Links")
    st.markdown("[📚 API Documentation](http://localhost:8000/docs)")
    st.markdown("[📈 Metrics](http://localhost:8000/metrics)")
    st.markdown("[🖥️ VNC Desktop](http://localhost:6080/vnc.html)")
    st.markdown("[💻 Code Server](http://localhost:8443)")

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💻 Code Generation",
    "🐛 Debug",
    "🔧 Refactor",
    "🧪 Test Generation",
    "📝 Documentation"
])

with tab1:
    st.header("Code Generation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        task = st.text_area(
            "Describe what you want to build:",
            height=150,
            placeholder="Example: Create a REST API with FastAPI for managing a todo list with CRUD operations, authentication, and PostgreSQL database..."
        )
    
    with col2:
        language = st.selectbox(
            "Programming Language",
            ["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++", "Ruby"]
        )
        
        framework = st.text_input(
            "Framework (optional)",
            placeholder="e.g., FastAPI, React, Django, Express"
        )
        
        style = st.selectbox(
            "Coding Style",
            ["Clean Code", "Functional", "Object-Oriented", "Procedural"]
        )
    
    if st.button("🚀 Generate Code", type="primary", use_container_width=True):
        if task and api_key:
            with st.spinner("🤔 AI is generating code..."):
                try:
                    context = {
                        "language": language,
                        "framework": framework,
                        "style": style
                    }
                    
                    response = requests.post(
                        "http://localhost:8000/execute",
                        json={"task": task, "context": context},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result["status"] == "success":
                            st.success("✅ Code generated successfully!")
                            
                            # Display execution time
                            if result.get("execution_time"):
                                st.info(f"⏱️ Execution time: {result['execution_time']:.2f} seconds")
                            
                            # Display the generated code
                            st.code(result.get("response", ""), language=language.lower())
                            
                            # Download button
                            st.download_button(
                                label="📥 Download Code",
                                data=result.get("response", ""),
                                file_name=f"generated_code.{language.lower()}",
                                mime="text/plain"
                            )
                        else:
                            st.error(f"❌ Error: {result.get('error')}")
                    else:
                        st.error(f"❌ API Error: {response.status_code}")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            if not api_key:
                st.warning("⚠️ Please configure your API key in the sidebar")
            if not task:
                st.warning("⚠️ Please describe what you want to build")

with tab2:
    st.header("Debug Issue")
    
    error_msg = st.text_area(
        "Error Message:",
        height=100,
        placeholder="Paste the error message here..."
    )
    
    stack_trace = st.text_area(
        "Stack Trace (optional):",
        height=150,
        placeholder="Paste the stack trace here..."
    )
    
    code_context = st.text_area(
        "Code Context (optional):",
        height=200,
        placeholder="Paste relevant code here..."
    )
    
    if st.button("🔍 Debug", type="primary", use_container_width=True):
        if error_msg and api_key:
            with st.spinner("🔍 Analyzing and debugging..."):
                debug_task = f"""Debug this error:
                Error: {error_msg}
                Stack Trace: {stack_trace}
                Code Context: {code_context}
                
                Please identify the root cause and provide a solution."""
                
                try:
                    response = requests.post(
                        "http://localhost:8000/execute",
                        json={"task": debug_task},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result["status"] == "success":
                            st.success("✅ Debug analysis complete!")
                            st.markdown(result.get("response", ""))
                        else:
                            st.error(f"❌ Error: {result.get('error')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            if not api_key:
                st.warning("⚠️ Please configure your API key")
            if not error_msg:
                st.warning("⚠️ Please provide an error message")

with tab3:
    st.header("Code Refactoring")
    
    code_to_refactor = st.text_area(
        "Paste your code here:",
        height=300,
        placeholder="Paste the code you want to refactor..."
    )
    
    refactor_type = st.selectbox(
        "Refactoring Type",
        ["Improve Readability", "Optimize Performance", "Extract Functions",
         "Remove Duplication", "Add Type Hints", "Add Error Handling",
         "Convert to Async", "Apply Design Patterns"]
    )
    
    if st.button("♻️ Refactor", type="primary", use_container_width=True):
        if code_to_refactor and api_key:
            with st.spinner("♻️ Refactoring code..."):
                refactor_task = f"""Refactor this code with focus on {refactor_type}:
                
                {code_to_refactor}
                
                Provide the refactored code with explanations of changes made."""
                
                try:
                    response = requests.post(
                        "http://localhost:8000/execute",
                        json={"task": refactor_task},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result["status"] == "success":
                            st.success("✅ Code refactored successfully!")
                            st.code(result.get("response", ""))
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

with tab4:
    st.header("Test Generation")
    
    code_to_test = st.text_area(
        "Paste your code here:",
        height=300,
        placeholder="Paste the code you want to generate tests for..."
    )
    
    test_framework = st.selectbox(
        "Test Framework",
        ["pytest", "unittest", "jest", "mocha", "JUnit", "RSpec", "Go test"]
    )
    
    test_type = st.multiselect(
        "Test Types",
        ["Unit Tests", "Integration Tests", "Edge Cases", "Error Scenarios",
         "Performance Tests", "Security Tests"],
        default=["Unit Tests", "Edge Cases"]
    )
    
    if st.button("🧪 Generate Tests", type="primary", use_container_width=True):
        if code_to_test and api_key:
            with st.spinner("🧪 Generating tests..."):
                test_task = f"""Generate {', '.join(test_type)} using {test_framework} for this code:
                
                {code_to_test}
                
                Include comprehensive test cases with assertions."""
                
                try:
                    response = requests.post(
                        "http://localhost:8000/execute",
                        json={"task": test_task},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result["status"] == "success":
                            st.success("✅ Tests generated successfully!")
                            st.code(result.get("response", ""))
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

with tab5:
    st.header("Documentation Generation")
    
    code_to_document = st.text_area(
        "Paste your code here:",
        height=300,
        placeholder="Paste the code you want to document..."
    )
    
    doc_type = st.selectbox(
        "Documentation Type",
        ["API Documentation", "Code Comments", "README", "Docstrings",
         "Technical Specification", "User Guide", "Architecture Overview"]
    )
    
    doc_format = st.selectbox(
        "Format",
        ["Markdown", "reStructuredText", "HTML", "JSDoc", "JavaDoc", "XML"]
    )
    
    if st.button("📝 Generate Documentation", type="primary", use_container_width=True):
        if code_to_document and api_key:
            with st.spinner("📝 Generating documentation..."):
                doc_task = f"""Generate {doc_type} in {doc_format} format for this code:
                
                {code_to_document}
                
                Make it comprehensive and well-structured."""
                
                try:
                    response = requests.post(
                        "http://localhost:8000/execute",
                        json={"task": doc_task},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result["status"] == "success":
                            st.success("✅ Documentation generated successfully!")
                            st.markdown(result.get("response", ""))
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Made with ❤️ using Claude Computer Use API</p>
        <p>Version 1.0.0 | © 2024 Computer Use Coding Assistant</p>
    </div>
    """,
    unsafe_allow_html=True
)
