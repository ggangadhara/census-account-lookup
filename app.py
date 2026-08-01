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

# Modern UI CSS Styling with STRICT PURE WHITE BACKGROUND Enforced
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* STRICTLY ENFORCE PURE WHITE BACKGROUND GLOBALLY */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    /* Enforce Dark Text for Streamlit Widgets/Labels in case Dark Mode is default */
    label[data-testid="stWidgetLabel"] p {
        color: #0F172A !important;
        font-weight: 600 !important;
    }
    input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* Main Container */
    .main {
        max-width: 740px;
        padding-top: 1.5rem;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit default top spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        background-color: #FFFFFF !important;
    }

    /* Top Badge */
    .hero-badge {
        display: inline-block;
        background: #EEF2FF;
        color: #4F46E5;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 20px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 12px;
        border: 1px solid #E0E7FF;
    }

    /* H1 & H2 Header Typography */
    .header-h1 {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.5px;
        margin-bottom: 0.4rem;
        line-height: 1.2;
    }
    .header-h2 {
        font-size: 1.15rem;
        font-weight: 500;
        color: #64748B;
        margin-bottom: 2rem;
        line-height: 1.5;
    }

    /* Modern Result Card on Pure White */
    .result-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 28px;
        margin-top: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
        position: relative;
        overflow: hidden;
    }
    .result-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #4F46E5, #3B82F6);
    }
    
    /* Result Card Header & Role Badge */
    .result-header-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 16px;
        margin-bottom: 18px;
        flex-wrap: wrap;
        gap: 10px;
    }
    .result-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }
    .role-badge {
        font-size: 0.85rem;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 20px;
        text-transform: capitalize;
    }
    .role-supervisor {
        background-color: #EEF2FF;
        color: #4338CA;
        border: 1px solid #C7D2FE;
    }
    .role-enumerator {
        background-color: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
    }
    .role-default {
        background-color: #F1F5F9;
        color: #475569;
        border: 1px solid #CBD5E1;
    }

    /* Rows and Text Layout */
    .result-row {
        display: flex;
        flex-direction: column;
        margin-bottom: 14px;
        font-size: 1.15rem;
        color: #1E293B;
        line-height: 1.4;
    }
    .result-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #64748B;
        margin-bottom: 3px;
    }
    .result-value {
        font-weight: 500;
        color: #0F172A;
    }
    .account-code {
        font-family: 'Courier New', Courier, monospace;
        font-weight: 700;
        color: #1E40AF;
        background: #EFF6FF;
        padding: 2px 8px;
        border-radius: 6px;
        display: inline-block;
        width: fit-content;
    }

    /* Modern Footer */
    .footer-credit {
        margin-top: 4rem;
        padding-top: 1.5rem;
        border-top: 1px solid #E2E8F0;
        text-align: center;
        font-size: 0.9rem;
        color: #64748B;
        line-height: 1.7;
        background-color: #FFFFFF !important;
    }
    .footer-name {
        font-weight: 600;
        color: #334155;
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

# 1. Modern Page Headers
st.markdown(
    """
    <div>
        <div class="hero-badge">Official Remuneration Portal</div>
        <div class="header-h1">Census 2027 Malavalli Rural</div>
        <div class="header-h2">Account Details of Enumerators and Supervisors for Remuneration HLO work</div>
    </div>
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

# 3. Modern Search Interface
if not df.empty:
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
                    role = str(row.get("Role", "N/A")).strip()
                    role_lower = role.lower()

                    # Assign modern badge styles based on Role
                    if "supervisor" in role_lower:
                        badge_class = "role-badge role-supervisor"
                    elif "enumerator" in role_lower:
                        badge_class = "role-badge role-enumerator"
                    else:
                        badge_class = "role-badge role-default"

                    # Render modern result card
                    st.markdown(
                        f"""
                        <div class="result-card">
                            <div class="result-header-wrapper">
                                <div class="result-header">👤 {row.get('Name', 'N/A')}</div>
                                <div class="{badge_class}">{role}</div>
                            </div>
                            <div class="result-row">
                                <span class="result-label">Mobile Number</span>
                                <span class="result-value">{row.get('Mobile Number', row.get('Clean_Mobile', 'N/A'))}</span>
                            </div>
                            <div class="result-row">
                                <span class="result-label">Circle Number</span>
                                <span class="result-value">{row.get('Circle No', 'N/A')}</span>
                            </div>
                            <div class="result-row">
                                <span class="result-label">Account Number</span>
                                <span class="account-code">{row.get('Account No', 'N/A')}</span>
                            </div>
                            <div class="result-row">
                                <span class="result-label">IFSC Code</span>
                                <span class="account-code">{row.get('IFSC Code', 'N/A')}</span>
                            </div>
                            <div class="result-row">
                                <span class="result-label">Bank Name</span>
                                <span class="result-value">{row.get('Bank Name', 'N/A')}</span>
                            </div>
                            <div class="result-row">
                                <span class="result-label">Branch Name</span>
                                <span class="result-value">{row.get('Branch Name', 'N/A')}</span>
                            </div>
                            <div class="result-row">
                                <span class="result-label">School / Office Address</span>
                                <span class="result-value">{row.get('Supervior/Enumerator School/Office Address', 'N/A')}</span>
                            </div>
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
        <span class="footer-name">Design and developed by Gangadhar</span><br>
        Statistical Inspector, Taluk Office Malavalli | Contact: <strong>9008737033</strong>
    </div>
    """,
    unsafe_allow_html=True,
)
