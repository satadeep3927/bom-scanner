import io
import os
import tempfile

import pandas as pd
import streamlit as st

from client import LLMClient
from common.settings import settings

# Load settings
LLM_API_KEY = settings.GITHUB_COPILOT_TOKEN
LLM_API_BASE = settings.LLM_API_BASE
LLM_MODEL = settings.LLM_MODEL

client = LLMClient(ai_model=LLM_MODEL)

# App title
st.set_page_config(page_title="Electrical Component Analyzer", layout="wide")

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

# Authentication function
def check_credentials(username: str, password: str) -> bool:
    """Verify username and password against settings."""
    credentials = settings.LOGIN_CREDENTIALS
    if credentials and username in credentials:
        return credentials[username] == password
    return False

# Login page
if not st.session_state.authenticated:
    # Center the login form using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Card-like container with styling
        st.markdown("""
        <style>
        .stForm {
            max-width: 400px;
            margin: auto;
            padding: 50px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        

        with st.form("login_form"):
            st.markdown("<h1 style='text-align: center;'> Login</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #666;'>Please enter your credentials to access the Electrical Component Analyzer</p>", unsafe_allow_html=True)
        
            username = st.text_input("Username (Email)", placeholder="user@example.com")
            password = st.text_input("Password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if submit_button:
                if check_credentials(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.stop()  # Stop execution if not authenticated

# Logout button in sidebar
with st.sidebar:
    st.markdown(f"**Logged in as:** {st.session_state.username}")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    st.divider()

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
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "selected_components" not in st.session_state:
    st.session_state.selected_components = []
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None
if "temp_file_path" not in st.session_state:
    st.session_state.temp_file_path = None
if "selected_options" not in st.session_state:
    st.session_state.selected_options = []

# Save uploaded file to temp location (but don't analyze yet)
if uploaded_file:
    # Check if this is a new file
    if st.session_state.last_uploaded_file != uploaded_file.name:
        st.success(
            "File uploaded successfully! Select analysis mode and click 'Analyze Diagram' to start."
        )

        # Clean up old temp file if exists
        if st.session_state.temp_file_path and os.path.exists(
            st.session_state.temp_file_path
        ):
            os.remove(st.session_state.temp_file_path)

        # Save uploaded file to a temporary path
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(uploaded_file.name)[1]
        ) as tmp_file:
            tmp_file.write(uploaded_file.read())
            st.session_state.temp_file_path = tmp_file.name
            st.session_state.last_uploaded_file = uploaded_file.name
            # Clear previous analysis when new file uploaded
            st.session_state.analysis_result = None
else:
    # Clear the session state if no file is uploaded
    if st.session_state.temp_file_path and os.path.exists(
        st.session_state.temp_file_path
    ):
        os.remove(st.session_state.temp_file_path)
    st.session_state.last_uploaded_file = None
    st.session_state.temp_file_path = None
    st.session_state.analysis_result = None

# Add Analyze button
if uploaded_file and st.session_state.temp_file_path:
    if st.button("🔍 Analyze Diagram", type="primary", use_container_width=True):
        with st.spinner("Analyzing the diagram..."):
            result = client.generate_bom_summary(
                st.session_state.temp_file_path, analysis_mode
            )
            st.session_state.analysis_result = result
        st.success("✅ Analysis complete!")

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
            f"{item['Item']} - {item['Description']}" for item in all_components
        ]

        # Handle button clicks before rendering widgets
        if "button_clicked" not in st.session_state:
            st.session_state.button_clicked = None

        # Component selection in same row
        col1, col2, col3 = st.columns([5, 1, 1])

        with col1:
            # 1. Use session_state as the SINGLE source of truth
            if "selected_options" not in st.session_state:
                st.session_state.selected_options = []

            # 2. Multiselect with NO key, default from session_state
            selected_options = st.multiselect(
                "Choose components to include in Bill of Materials:",
                options=component_options,
                default=st.session_state.selected_options,
                help="Select the components you want to include in your BOM",
            )

            # 3. CRITICAL: Immediately sync back any user change
            st.session_state.selected_options = selected_options

        with col2:
            st.markdown(
                "<div style='padding-top: 28px;'></div>", unsafe_allow_html=True
            )
            if st.button("Select All", use_container_width=True, key="select_all_btn"):
                st.session_state.selected_options = component_options.copy()
                st.rerun()

        with col3:
            st.markdown(
                "<div style='padding-top: 28px;'></div>", unsafe_allow_html=True
            )
            if st.button("Clear All", use_container_width=True, key="clear_all_btn"):
                st.session_state.selected_options = []
                st.rerun()

        # Update session state with current selection
        if selected_options != st.session_state.selected_options:
            st.session_state.selected_options = selected_options

        # Update selected components in session state
        selected_indices = [
            component_options.index(opt)
            for opt in selected_options
            if opt in component_options
        ]
        st.session_state.selected_components = [
            all_components[i] for i in selected_indices
        ]

        # Generate BOM button
        if st.button("📋 Generate Bill of Materials", type="primary"):
            if st.session_state.selected_components:
                st.subheader("📋 Bill of Materials")

                # Display selected components in a table
                st.dataframe(st.session_state.selected_components)

                st.success(
                    f"✅ BOM Generated: {len(st.session_state.selected_components)} items selected"
                )

                # Download button for CSV
                df = pd.DataFrame(st.session_state.selected_components)
                csv = df.to_csv(index=False)

                st.download_button(
                    label="📥 Download BOM as CSV",
                    data=csv,
                    file_name="electrical_bom.csv",
                    mime="text/csv",
                    key="download-csv",
                )

                # Download button for Excel
                excel_buffer = io.BytesIO()
                df.to_excel(excel_buffer, index=False, engine="openpyxl")
                excel_data = excel_buffer.getvalue()

                st.download_button(
                    label="📊 Download BOM as Excel",
                    data=excel_data,
                    file_name="electrical_bom.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download-excel",
                )
            else:
                st.warning("⚠️ Please select at least one component for the BOM.")
    else:
        st.error(
            "❌ No components were detected in the uploaded diagram. Please try a different image or analysis mode."
        )
