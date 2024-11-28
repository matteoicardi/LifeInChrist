import streamlit as st
import markdown
# import pdfkit
from datetime import datetime
import os
import pickle
from parsers import *
from rota_generator import *
from utils import *

# Define absolute paths for the data directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PEOPLE_FOLDER = os.path.join(BASE_DIR, "data/people")
ROLES_FOLDER = os.path.join(BASE_DIR, "data/roles")

# Ensure the directories exist
os.makedirs(PEOPLE_FOLDER, exist_ok=True)
os.makedirs(ROLES_FOLDER, exist_ok=True)

new_person_template = """Name: 
Surname: 
Phone: 
Role: 
Mass: 
AvoidWeeks: 
AvoidDates: 
With: 
"""

new_person_example = """Name: John
Surname: Doe
Phone: 123456789
Role: Reader, EM, Steward
Mass: Sat, Sun, Extra  (Extra are masses not on Sat or Sun)
AvoidWeeks: 2, 4  (Weeks to avoid, -1 for last week of the month)
AvoidDates: 01/01/2022-31/01/2022, 01/07/2022-31/07/2022  (Dates to avoid)
With: Jane, Mary  (People to be scheduled with)
NB: CAREFULLY FOLLOW THIS FORMAT, NOTICE THE SPACES AND COMMAS AND HYPHENS
"""

new_role_template = """Role: 
Sat: 
Sun: 
ExtraDates: 
"""

new_role_example = """Role: Reader
Sat: 1 (Number of people required)
Sun: 1 (Number of people required)
ExtraDates: 01/01/2022 (2), 01/07/2022 (1) (Extra masses with number of people required)
NB: THE SPELLING OF THE ROLE SHOULD MATCH THE ROLE IN THE PERSON FILES
"""


def main():
    st.title("Parish Rota Generator")

    # Section to manage people files
    st.header("Manage People")
    
    # show example of how to write a new person file
    st.markdown("### New Person File Example")
    st.code(new_person_example, language="text")
    st.markdown("### Modify existing person file")
    people_files = list_files(PEOPLE_FOLDER)
    selected_person_file = st.selectbox("Select a person file to edit", people_files)
    if selected_person_file:
        person_content = read_file(os.path.join(PEOPLE_FOLDER, selected_person_file))
        updated_person_content = st.text_area("Edit person file", person_content)
        if st.button("Save Person"):
            write_file(os.path.join(PEOPLE_FOLDER, selected_person_file), updated_person_content)
            st.success("Person file saved.")
        if st.button("Delete Person"):
            delete_file(os.path.join(PEOPLE_FOLDER, selected_person_file))
            st.success("Person file deleted.")
            st.rerun()

    st.markdown("### Add New Person")
    new_person_name = st.text_input("New person file name (without extension)")
    new_person_content = st.text_area("New person file content", new_person_template)
    if st.button("Add New Person"):
        if new_person_name:
            write_file(os.path.join(PEOPLE_FOLDER, f"{new_person_name}.txt"), new_person_content)
            st.success("New person file added.")
            st.rerun()

    # Section to manage roles files
    st.header("Manage Roles")
    
    # show example of how to write a new role file
    st.markdown("### New Role File Example")
    st.code(new_role_example, language="text")
    st.markdown("### Modify existing role file")
    roles_files = list_files(ROLES_FOLDER)
    selected_role_file = st.selectbox("Select a role file to edit", roles_files)
    if selected_role_file:
        role_content = read_file(os.path.join(ROLES_FOLDER, selected_role_file))
        updated_role_content = st.text_area("Edit role file", role_content)
        if st.button("Save Role"):
            write_file(os.path.join(ROLES_FOLDER, selected_role_file), updated_role_content)
            st.success("Role file saved.")
        if st.button("Delete Role"):
            delete_file(os.path.join(ROLES_FOLDER, selected_role_file))
            st.success("Role file deleted.")
            st.rerun()

    st.markdown("### Add New Role")
    new_role_name = st.text_input("New role file name (without extension)")
    new_role_content = st.text_area("New role file content", new_role_template)
    if st.button("Add New Role"):
        if new_role_name:
            write_file(os.path.join(ROLES_FOLDER, f"{new_role_name}.txt"), new_role_content)
            st.success("New role file added.")
            st.rerun()

    st.header("Generate Rota")

    # Input date range
    date_range = st.text_input("Date range (DD/MM/YYYY-DD/MM/YYYY)", "")    
    # Input roles
    roles_input = st.text_input("Rota only for the following roles (comma-separated, optional)", "")
    
    # Load people and roles
    people = read_people(PEOPLE_FOLDER)
    roles = read_roles(ROLES_FOLDER)

    # Add a button to generate the rota
    if st.button("Generate Rota"):
        if not date_range:
            st.warning("Please enter a date range.")
            return

        roles_list = [role.strip() for role in roles_input.split(",")] if roles_input else []

        # Parse the date range
        try:
            start_str, end_str = date_range.split("-")
            start_date = datetime.strptime(start_str.strip(), "%d/%m/%Y")
            end_date = datetime.strptime(end_str.strip(), "%d/%m/%Y")
        except ValueError:
            st.error("Invalid date range format. Use DD/MM/YYYY-DD/MM/YYYY.")
            return

        # Filter roles if specified
        if roles_list:
            roles = [role for role in roles if role.name in roles_list]

        if not roles:
            st.error("No roles found. Check the roles folder or spell the roles correctly as argument of the function.")
            return

        # Compute weekends
        weekends = compute_weekends(start_date, end_date)
        # Add special dates
        weekends.extend(compute_special_dates(start_date, end_date, roles))
        # order weekends by date
        weekends.sort(key=lambda x: x[2])


        # Generate the rota
        rota, duty_count, duty = generate_rota(people, roles, weekends)

        # Generate filename based on the date range and make it relative to the current directory
        output_filename = os.path.join(BASE_DIR, generate_filename(start_date, end_date))
        # create the clean filename using start and end dates with no folder path
        st.session_state["filename"] = os.path.basename(output_filename)

        # Export the rota to Markdown
        markdown_text = export_to_markdown(rota, date_range, duty_count, duty)
        with open(output_filename, "w") as file:
            file.write(markdown_text)
        st.success(f"Rota successfully exported to {output_filename}")
        st.session_state["output_filename"] = output_filename

        # HTML
        output_html_filename = output_filename.replace(".md", ".html")
        try:
            html_text = markdown.markdown(markdown_text)
            with open(output_html_filename, "w") as file:
                file.write(html_text)
            st.session_state["output_html_filename"] = output_html_filename
            st.success(f"HTML successfully generated: {output_html_filename}")
        except Exception as e:
            st.error(f"Error generating HTML: {e}")
            st.session_state["output_html_filename"] = None
            
        # PDF
        output_pdf_filename = output_filename.replace(".md", ".pdf")
        try:
            # pdfkit.from_string(html_text, output_pdf_filename)
            convert_md_to_pdf(output_filename, output_pdf_filename)
            st.session_state["output_pdf_filename"] = output_pdf_filename
            st.success(f"PDF successfully generated: {output_pdf_filename}")
        except Exception as e:
            st.error(f"Error generating PDF: {e}")
            st.session_state["output_pdf_filename"] = None


        # Store filenames in session state to keep download buttons visible
        st.session_state["output_html_filename"] = output_html_filename
        
    # Display download buttons if files are available
    if st.session_state.get("output_filename"):
        with open(st.session_state["output_filename"], "r") as file:
            st.download_button("Download Markdown", file, file_name=st.session_state["filename"]+".md")

    if st.session_state.get("output_pdf_filename"):
        with open(st.session_state["output_pdf_filename"], "rb") as file:
            st.download_button("Download PDF", file, file_name=st.session_state["filename"]+".pdf")
    
    if st.session_state.get("output_html_filename"):
        with open(st.session_state["output_html_filename"], "r") as file:
            st.download_button("Download HTML", file, file_name=st.session_state["filename"]+".html")

    # Section to download and upload roles data
    st.header("Download/Upload Data")
    
    # Download People Data
    # people_binary = save_people_binary(people)
    st.download_button("Download People Data", data=pickle.dumps(people), file_name="people.rota")

    # Download Roles Data
    # roles_binary = save_roles_binary(roles)
    st.download_button("Download Roles Data", data=pickle.dumps(roles), file_name="roles.rota")
    
    # Upload People or Roles Data using pickle files saved above
    uploaded_file = st.file_uploader("Upload People or Roles Data", type=["rota"])
    if uploaded_file:
        data = pickle.load(uploaded_file)
        if isinstance(data[0], Person):
            for person in data:
                person.write(os.path.join(PEOPLE_FOLDER, f"{person.name}_{person.surname}.txt"))
            st.success("People data uploaded and files created.")
        elif isinstance(data[0], Role):
            for role in data:
                role.write(os.path.join(ROLES_FOLDER, f"{role.name}.txt"))
            st.success("Roles data uploaded and files created.")
        else:
            st.error("Invalid data format.")
        st.rerun()
    
    # Remove all data files
    if st.button("Remove All Data Files"):
        # Confirm the action
        if st.button("Click here to confirm deletion of all data files"):
            for file in people_files:
                delete_file(os.path.join(PEOPLE_FOLDER, file))
            for file in roles_files:
                delete_file(os.path.join(ROLES_FOLDER, file))
            st.success("All data files removed.")
            st.rerun()
                
        
if __name__ == "__main__":
    main()