import io
import os
import tempfile

import pandas as pd
import streamlit as st

from client import LLMClient
from settings import LLM_API_BASE, LLM_API_KEY, LLM_MODEL

client = LLMClient(api_key=LLM_API_KEY, api_base=LLM_API_BASE, ai_model=LLM_MODEL)

# App title
st.set_page_config(page_title="Electrical Component Analyzer", layout="wide")
st.title("🔌 Electrical Diagram Component Analyzer")

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

analysis_mode = st.sidebar.selectbox(
    "Select Analysis Mode",
    ["default", "power_quality", "load_analysis", "fault_detection"],
)

# File uploader
uploaded_file = st.file_uploader(
    "📤 Upload Electrical Diagram (JPG, PNG, PDF)", type=["jpg", "jpeg", "png", "pdf"]
)

# Initialize session state for storing analysis results
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'selected_components' not in st.session_state:
    st.session_state.selected_components = []

# Run analysis
if uploaded_file:
    st.success("File uploaded. Processing...")

    # Save uploaded file to a temporary path
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=os.path.splitext(uploaded_file.name)[1]
    ) as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name

    # Run the analysis
    with st.spinner("Analyzing the diagram..."):
        result = client.generate_bom_summary(temp_path, analysis_mode)
        st.session_state.analysis_result = result

    # Clean up temp file
    os.remove(temp_path)

# Display analysis results if available
if st.session_state.analysis_result:
    result = st.session_state.analysis_result

    # Show raw response
    with st.expander("🧾 Raw LLM Output (JSON)", expanded=False):
        st.code(result["raw_analysis"], language="json")

    # Component Selection Interface
    st.subheader("🎯 Select Components for BOM")

    # Get all detected components
    all_components = result["bom_items"]

    if all_components:
        # Create options for multiselect
        component_options = [
            f"{item['Item']} - {item['Description']}"
            for item in all_components
        ]

        # Component selection
        selected_options = st.multiselect(
            "Choose components to include in Bill of Materials:",
            options=component_options,
            default=component_options,  # Select all by default
            help="Select the components you want to include in your BOM"
        )

        # Update selected components in session state
        selected_indices = [component_options.index(opt) for opt in selected_options]
        st.session_state.selected_components = [
            all_components[i] for i in selected_indices
        ]

        # Generate BOM button
        if st.button("📋 Generate Bill of Materials", type="primary"):
            if st.session_state.selected_components:
                st.subheader("📋 Bill of Materials")

                # Display selected components in a table
                st.dataframe(st.session_state.selected_components)

                st.success(f"✅ BOM Generated: {len(st.session_state.selected_components)} items selected")

                # Download button for CSV
                import pandas as pd

                df = pd.DataFrame(st.session_state.selected_components)
                csv = df.to_csv(index=False)

                st.download_button(
                    label="📥 Download BOM as CSV",
                    data=csv,
                    file_name="electrical_bom.csv",
                    mime="text/csv",
                    key="download-csv"
                )

                # Download button for Excel
                excel_buffer = io.BytesIO()
                df.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_data = excel_buffer.getvalue()

                st.download_button(
                    label="📊 Download BOM as Excel",
                    data=excel_data,
                    file_name="electrical_bom.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download-excel"
                )
            else:
                st.warning("⚠️ Please select at least one component for the BOM.")
    else:
        st.error("❌ No components were detected in the uploaded diagram. Please try a different image or analysis mode.")
