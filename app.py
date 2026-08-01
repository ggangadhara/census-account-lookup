import os
import pandas as pd
import pdfplumber
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Census 2027 Malavalli Rural - Account Lookup",
    page_icon="🏛️",
    layout="centered",
)

# Professional CSS styling with larger fonts for search details
st.markdown(
    """
    <style>
    /* Main container width and clean font sizing */
    .main {
        max-width: 720px;
        padding-top: 1rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Clean, uniform styling for H1 and H2 */
    .header-h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }
    .header-h2 {
        font-size: 1.15rem;
        font-weight: 500;
        color: #4B5563;
        margin-bottom: 1.5rem;
        line-height: 1.4;
    }
    
    /* Increased font size for result cards and uniform typography */
    .result-card {
        background-color: #F9FAFB;
        border: 1px solid #D1D5DB;
        border-radius: 10px;
        padding: 24px;
        margin-top: 20px;
        font-size: 1.15rem; /* Increased font size */
        color: #1F2937;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .result-header {
        font-size: 1.45rem; /* Increased name header size */
        font-weight: 700;
        color: #111827;
        border-bottom: 2px solid #E5E7EB;
        padding-bottom: 10px;
        margin-bottom: 14px;
    }
    .result-row {
        margin-bottom: 10px;
        line-height: 1.6;
    }
    .result-label {
        font-weight: 600;
        color: #374151;
    }
    
    /* Footer credit styling */
    .footer-credit {
        margin-top: 3.5rem;
        padding-top: 1.2rem;
        border-top: 1px solid #E5E7EB;
        text-align: center;
        font-size: 0.9rem;
        color: #6B7280;
        line-height: 1.6;
    }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Extracting and processing PDF data...")
def load_and_parse_pdf(pdf_source):
    all_rows = []
    headers = None

    with pdfplumber.open(pdf_source) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    cleaned_row = [
                        str(cell).replace("\n", " ").strip() if cell else ""
                        for cell in row
                    ]

                    if headers is None and "Mobile Number" in cleaned_row:
                        headers = cleaned_row
                        continue

                    if "Mobile Number" in cleaned_row or "Role" in cleaned_row:
                        continue

                    if any(cleaned_row):
                        all_rows.append(cleaned_row)

    if not all_rows or headers is None:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows, columns=headers)
    df.columns = df.columns.str.strip()

    if "Circle No" in df.columns:
        df["Circle No"] = df["Circle No"].replace("", pd.NA).ffill()

    if "Mobile Number" in df.columns:
        df["Clean_Mobile"] = (
            df["Mobile Number"].str.replace(r"\D", "", regex=True).str[-10:]
        )

    return df


# Callback function to clear the search input box
def clear_input():
    st.session_state["phone_input"] = ""
    st.session_state["search_triggered"] = False


# Initialize session state variables
if "phone_input" not in st.session_state:
    st.session_state["phone_input"] = ""
if "search_triggered" not in st.session_state:
    st.session_state["search_triggered"] = False

# 1. Custom Page Headers (H1 & H2)
st.markdown(
    """
    <div class="header-h1">Census 2027 Malavalli Rural</div>
    <div class="header-h2">Account Details of Enumerators and Supervisors for Remuneration HLO work</div>
    """,
    unsafe_allow_html=True,
)

# 2. Load PDF Data
pdf_filename = "Census Bank Details Final.pdf"
df = pd.DataFrame()

if os.path.exists(pdf_filename):
    df = load_and_parse_pdf(pdf_filename)
else:
    uploaded_file = st.file_uploader(
        "Upload 'Census Bank Details Final.pdf'",
        type=["pdf"],
        help="Upload the official census bank details PDF document.",
    )
    if uploaded_file is not None:
        df = load_and_parse_pdf(uploaded_file)

# 3. Search Bar & Buttons
if not df.empty:
    # Text input without placeholder background text
    phone_input = st.text_input(
        "Mobile Number",
        max_chars=10,
        key="phone_input",
        help="Please enter exactly 10 numeric digits.",
    )

    # Search and Clear buttons side by side
    col1, col2, col3 = st.columns([1.5, 1.5, 4])
    with col1:
        if st.button("Search", type="primary", use_container_width=True):
            st.session_state["search_triggered"] = True
    with col2:
        st.button(
            "Clear",
            on_click=clear_input,
            type="secondary",
            use_container_width=True,
        )

    # Trigger search on button click or when user presses Enter
    if st.session_state["search_triggered"] or (
        phone_input and len(phone_input) == 10
    ):
        search_term = "".join(filter(str.isdigit, phone_input))

        # Enforce exactly 10 digits
        if len(search_term) != 10:
            st.warning(
                "⚠️ Please enter exactly 10 digits for the mobile number."
            )
        else:
            results = df[df["Clean_Mobile"] == search_term]

            if not results.empty:
                st.success(f"Found {len(results)} matching record(s).")
                for _, row in results.iterrows():
                    # Render record with larger font size & included Mobile Number
                    st.markdown(
                        f"""
                        <div class="result-card">
                            <div class="result-header">👤 {row.get('Name', 'N/A')}</div>
                            <div class="result-row"><span class="result-label">Role:</span> {row.get('Role', 'N/A')}</div>
                            <div class="result-row"><span class="result-label">Mobile Number:</span> {row.get('Mobile Number', row.get('Clean_Mobile', 'N/A'))}</div>
                            <div class="result-row"><span class="result-label">Circle Number:</span> {row.get('Circle No', 'N/A')}</div>
                            <div class="result-row"><span class="result-label">Account Number:</span> {row.get('Account No', 'N/A')}</div>
                            <div class="result-row"><span class="result-label">IFSC Code:</span> {row.get('IFSC Code', 'N/A')}</div>
                            <div class="result-row"><span class="result-label">Bank Name:</span> {row.get('Bank Name', 'N/A')}</div>
                            <div class="result-row"><span class="result-label">Branch Name:</span> {row.get('Branch Name', 'N/A')}</div>
                            <div class="result-row"><span class="result-label">School / Office Address:</span> {row.get('Supervior/Enumerator School/Office Address', 'N/A')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.error(
                    "❌ No account details found for this mobile number. Please check the number and try again."
                )
else:
    st.info("Waiting for official PDF data to load.")

# 4. Footer Credit
st.markdown(
    """
    <div class="footer-credit">
        <strong>Design and developed by Gangadhar</strong><br>
        Statistical Inspector, Taluk Office Malavalli | Contact: 9008737033
    </div>
    """,
    unsafe_allow_html=True,
)
