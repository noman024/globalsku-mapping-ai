import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os
import logging
import json

# Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

if not API_URL or not API_KEY:
    st.error("API_URL and API_KEY must be configured in the .env file.")
    logging.error("API_URL and API_KEY are missing in the .env file.")
    st.stop()

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "app.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("Mapping app initialized.")

st.title("GlobalSKU - Mapping AI")
st.write("Upload source and destination files to extract column names and map them using AI.")

# File Upload Section
st.header("Step 1: Upload Source and Destination Files")

def enforce_string_types(df):
    """
    Converts all columns in the DataFrame to string types to ensure compatibility during serialization.
    """
    return df.astype(str)

def validate_uploaded_file(file, file_type):
    """
    Validate the uploaded file and log the status.
    """
    if not file:
        st.warning(f"Please upload a valid {file_type} file.")
        logging.warning(f"{file_type.capitalize()} file not uploaded.")
        return None
    logging.info(f"{file_type.capitalize()} file uploaded: {file.name}")
    return file

uploaded_source = validate_uploaded_file(st.file_uploader("Upload Source File (CSV/Excel)", type=["csv", "xlsx"]), "source")
uploaded_destination = validate_uploaded_file(st.file_uploader("Upload Destination File (CSV/Excel)", type=["csv", "xlsx"]), "destination")

source_columns = []
destination_columns = []

if uploaded_source:
    st.subheader("Source File Preview")
    source_file_ext = os.path.splitext(uploaded_source.name)[-1].lower()
    try:
        if source_file_ext == ".csv":
            source_df = pd.read_csv(uploaded_source)
        else:
            excel_source = pd.ExcelFile(uploaded_source)
            sheet_name = st.selectbox("Select Sheet for Source File", excel_source.sheet_names, key="source_sheet")
            source_df = pd.read_excel(uploaded_source, sheet_name=sheet_name)
        source_df = enforce_string_types(source_df)
        st.dataframe(source_df.head())
        source_columns = list(source_df.columns)
        st.write(f"Source Columns: {source_columns}")
        logging.info(f"Source file processed with columns: {source_columns}")
    except Exception as e:
        st.error(f"Error reading source file: {str(e)}")
        logging.error(f"Error reading source file: {str(e)}")
        st.stop()

if uploaded_destination:
    st.subheader("Destination File Preview")
    destination_file_ext = os.path.splitext(uploaded_destination.name)[-1].lower()
    try:
        if destination_file_ext == ".csv":
            destination_df = pd.read_csv(uploaded_destination)
        else:
            excel_destination = pd.ExcelFile(uploaded_destination)
            sheet_name = st.selectbox("Select Sheet for Destination File", excel_destination.sheet_names, key="destination_sheet")
            destination_df = pd.read_excel(uploaded_destination, sheet_name=sheet_name)
        destination_df = enforce_string_types(destination_df)
        st.dataframe(destination_df.head())
        destination_columns = list(destination_df.columns)
        st.write(f"Destination Columns: {destination_columns}")
        logging.info(f"Destination file processed with columns: {destination_columns}")
    except Exception as e:
        st.error(f"Error reading destination file: {str(e)}")
        logging.error(f"Error reading destination file: {str(e)}")
        st.stop()

# API Integration Section
st.header("Step 2: Generate Mapping")

if st.button("Generate Mapping"):
    if source_columns and destination_columns:
        with st.spinner("Processing... Please wait."):
            try:
                # Prepare the JSON payload
                payload = {
                    "source_table": {"columns": source_columns},
                    "destination_table": {"columns": destination_columns}
                }
                headers = {
                    "api_key": API_KEY,
                    "Content-Type": "application/json"
                }

                # Make the API call
                logging.info("Sending JSON payload to API for mapping...")
                response = requests.post(API_URL, json=payload, headers=headers)

                # Handle the API response
                if response.status_code == 200:
                    mappings = response.json().get("mappings", {})
                    st.subheader("Mapping Results")

                    # Display the mappings in a table
                    mapping_table = pd.DataFrame.from_dict(mappings, orient="index")
                    st.dataframe(mapping_table)

                    # Download Results
                    st.download_button(
                        label="Download Mapping Results as JSON",
                        data=json.dumps(mappings, indent=2),
                        file_name="mapping_results.json",
                        mime="application/json"
                    )
                    logging.info("Mapping results displayed and download option enabled.")
                else:
                    error_message = response.json().get("detail", "Unknown Error")
                    st.error(f"Failed to generate mapping: {response.status_code} - {error_message}")
                    logging.error(f"API error: {response.status_code} - {error_message}")
            except Exception as e:
                st.error(f"Error during API call: {str(e)}")
                logging.error(f"Error during API call: {str(e)}")
    else:
        st.warning("Please upload both source and destination files before generating mapping.")
        logging.warning("Attempt to generate mapping without both files uploaded.")


# import streamlit as st
# import requests
# import pandas as pd
# from dotenv import load_dotenv
# import os
# import logging
# import json

# # Load environment variables
# load_dotenv()
# API_URL = os.getenv("API_URL")
# API_KEY = os.getenv("API_KEY")

# if not API_URL or not API_KEY:
#     st.error("API_URL and API_KEY must be configured in the .env file.")
#     logging.error("API_URL and API_KEY are missing in the .env file.")
#     st.stop()

# def enforce_string_types(df):
#     """
#     Converts all columns in the DataFrame to string types to ensure compatibility during serialization.
#     """
#     return df.astype(str)

# # Configure logging
# log_dir = "logs"
# os.makedirs(log_dir, exist_ok=True)
# log_file = os.path.join(log_dir, "app.log")
# logging.basicConfig(
#     filename=log_file,
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
# )
# logging.info("Mapping app initialized.")

# st.title("GlobalSKU - Mapping AI")
# st.write("Upload source and destination files to map their columns using AI.")

# # File Upload Section
# st.header("Step 1: Upload Source and Destination Files")

# def validate_uploaded_file(file, file_type):
#     """
#     Validate the uploaded file and log the status.
#     """
#     if not file:
#         st.warning(f"Please upload a valid {file_type} file.")
#         logging.warning(f"{file_type.capitalize()} file not uploaded.")
#         return None
#     logging.info(f"{file_type.capitalize()} file uploaded: {file.name}")
#     return file

# uploaded_source = validate_uploaded_file(st.file_uploader("Upload Source File (CSV/Excel)", type=["csv", "xlsx"]), "source")
# uploaded_destination = validate_uploaded_file(st.file_uploader("Upload Destination File (CSV/Excel)", type=["csv", "xlsx"]), "destination")

# if uploaded_source and uploaded_destination:
#     logging.info("Both files uploaded successfully.")

#     # Read and display source file
#     st.subheader("Source File Preview")
#     source_file_ext = os.path.splitext(uploaded_source.name)[-1].lower()
#     try:
#         if source_file_ext == ".csv":
#             source_df = pd.read_csv(uploaded_source)
#         else:
#             excel_source = pd.ExcelFile(uploaded_source)
#             sheet_name = st.selectbox("Select Sheet for Source File", excel_source.sheet_names, key="source_sheet")
#             source_df = pd.read_excel(uploaded_source, sheet_name=sheet_name)
#         source_df = enforce_string_types(source_df)
#         st.dataframe(source_df.head())
#         logging.info(f"Source file processed with {len(source_df.columns)} columns.")
#     except Exception as e:
#         st.error(f"Error reading source file: {str(e)}")
#         logging.error(f"Error reading source file: {str(e)}")
#         st.stop()

#     # Read and display destination file
#     st.subheader("Destination File Preview")
#     destination_file_ext = os.path.splitext(uploaded_destination.name)[-1].lower()
#     try:
#         if destination_file_ext == ".csv":
#             destination_df = pd.read_csv(uploaded_destination)
#         else:
#             excel_destination = pd.ExcelFile(uploaded_destination)
#             sheet_name = st.selectbox("Select Sheet for Destination File", excel_destination.sheet_names, key="destination_sheet")
#             destination_df = pd.read_excel(uploaded_destination, sheet_name=sheet_name)
#         destination_df = enforce_string_types(destination_df)
#         st.dataframe(destination_df.head())
#         logging.info(f"Destination file processed with {len(destination_df.columns)} columns.")
#     except Exception as e:
#         st.error(f"Error reading destination file: {str(e)}")
#         logging.error(f"Error reading destination file: {str(e)}")
#         st.stop()
# else:
#     st.info("Please upload both source and destination files to proceed.")
#     logging.info("Waiting for both source and destination files.")

# # API Integration Section
# st.header("Step 2: Generate Mapping")

# if st.button("Generate Mapping"):
#     if uploaded_source and uploaded_destination:
#         with st.spinner("Processing... Please wait."):
#             try:
#                 # Reset file pointers
#                 uploaded_source.seek(0)
#                 uploaded_destination.seek(0)

#                 # Validate file extensions
#                 valid_extensions = [".csv", ".xlsx"]
#                 if not uploaded_source.name.endswith(tuple(valid_extensions)) or not uploaded_destination.name.endswith(tuple(valid_extensions)):
#                     st.error("Please upload valid CSV or Excel files.")
#                     logging.error("Invalid file extensions detected.")
#                     raise ValueError("Invalid file extensions.")

#                 # Prepare the files for the API call
#                 files = {
#                     "source_file": (uploaded_source.name, uploaded_source, "application/octet-stream"),
#                     "destination_file": (uploaded_destination.name, uploaded_destination, "application/octet-stream")
#                 }
#                 headers = {"api_key": API_KEY}

#                 # Make the API call
#                 logging.info("Sending files to API for mapping...")
#                 response = requests.post(API_URL, files=files, headers=headers)

#                 # Handle the API response
#                 if response.status_code == 200:
#                     mappings = response.json().get("mappings", {})
#                     st.subheader("Mapping Results")

#                     # Display the mappings in a table
#                     mapping_table = pd.DataFrame.from_dict(mappings, orient="index")
#                     st.dataframe(mapping_table)

#                     # Download Results
#                     st.download_button(
#                         label="Download Mapping Results as JSON",
#                         data=json.dumps(mappings, indent=2),
#                         file_name="mapping_results.json",
#                         mime="application/json"
#                     )
#                     logging.info("Mapping results displayed and download option enabled.")
#                 else:
#                     error_message = response.json().get("detail", "Unknown Error")
#                     st.error(f"Failed to generate mapping: {response.status_code} - {error_message}")
#                     logging.error(f"API error: {response.status_code} - {error_message}")
#             except Exception as e:
#                 st.error(f"Error during API call: {str(e)}")
#                 logging.error(f"Error during API call: {str(e)}")
#     else:
#         st.warning("Please upload both source and destination files before generating mapping.")
#         logging.warning("Attempt to generate mapping without both files uploaded.")
