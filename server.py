import streamlit as st
from client import LLMClient
from settings import LLM_API_KEY, LLM_API_BASE, LLM_MODEL
import tempfile
import os

client = LLMClient(api_key=LLM_API_KEY, api_base=LLM_API_BASE, ai_model=LLM_MODEL)
# App title
st.set_page_config(page_title="Electrical Component Analyzer", layout="wide")
st.title("🔌 Electrical Diagram Component Analyzer")

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

analysis_mode = st.sidebar.selectbox(
    "Select Analysis Mode",
    ["default", "power_quality", "load_analysis", "fault_detection"]
)

# File uploader
uploaded_file = st.file_uploader("📤 Upload Electrical Diagram (JPG, PNG, PDF)", type=["jpg", "jpeg", "png", "pdf"])

# Initialize client

# Run analysis
if uploaded_file:
    st.success("File uploaded. Processing...")

    # Save uploaded file to a temporary path
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name

    # Run the full pipeline
    with st.spinner("Analyzing the image..."):
        result = client.generate_bom_summary(temp_path, analysis_mode)

    # Show raw response
    with st.expander("🧾 Raw LLM Output (JSON)", expanded=False):
        st.code(result['raw_analysis'], language="json")

    # Show BOM table
    st.subheader("📋 Bill of Materials")
    st.dataframe(result['bom_items'])

    st.success(f"✅ Total Items Detected: {result['total_items']}")

    # Clean up
    os.remove(temp_path)
