import subprocess
import os

def export_to_markdown(rota, date_range, duty_count, duty):
    """
    Export the rota to a Markdown string with table format:
    Date | Role | Assigned
    """

    markdown_text = []

    # Title
    markdown_text.append(f"# Rota {date_range}\n")

    # Table header
    markdown_text.append("| Date | Role | Assigned |")
    markdown_text.append("|------|------|----------|")

    # Fill table rows
    for entry in rota:
        date_str = entry["date"].strftime("%A, %d %B %Y")
        roles = entry["roles"]

        first_row = True
        for role, people in roles.items():
            assigned_people = [p for p in people if p is not None]
            assigned_names = ", ".join(f"{p.name} {p.surname}" for p in assigned_people)
            unassigned_count = len(people) - len(assigned_people)
            unassigned = ", ".join(["Unassigned"] * unassigned_count)
            all_assigned = ", ".join(filter(None, [assigned_names, unassigned]))

            date_cell = date_str if first_row else ""
            markdown_text.append(f"| {date_cell} | **{role}** | {all_assigned or 'None'} |")
            first_row = False

        # Optional: Add a thick line between dates (looks clearer in long rotas)
        markdown_text.append("|------|------|----------|")

    markdown_text.append("\n---\n")

    # Duties summary
    markdown_text.append(f"\n# List of Duties {date_range}\n")

    for person in duty_count:
        markdown_text.append(f"### {person}")
        for role in duty_count[person]:
            count = duty_count[person][role]
            if count == 0:
                continue
            date_list = ", ".join(date.strftime("%d %B %Y") for date in duty[person][role])
            markdown_text.append(f"- {role}: {count} ({date_list})")
        markdown_text.append("")  # Blank line

    markdown_text.append("\n---\n")

    return "\n".join(markdown_text)

def convert_md_to_pdf(input_md_file, output_pdf_file):
    # Command to convert Markdown to PDF using pandoc
    command = [
        'pandoc',
        input_md_file,
        '-o', output_pdf_file,
        '--variable', 'fontsize=10pt',
        '--variable', 'geometry:margin=1in',
        '--variable', 'linestretch=1.0',
        '--pdf-engine', 'xelatex'
    ]

    
    # Run the command
    subprocess.run(command, check=True)
    

def generate_filename(start_date, end_date):
    # Format the date range as YYYY-MM-DD to use in the filename
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    filename = f"output/rota_{start_str}_to_{end_str}.md"
    return filename

def read_file(filepath):
    """Read the content of a file."""
    with open(filepath, "r") as file:
        return file.read()

def write_file(filepath, content):
    """Write content to a file."""
    with open(filepath, "w") as file:
        file.write(content)

def delete_file(filepath):
    """Delete a file."""
    os.remove(filepath)
    
    
def list_files(folder):
    return sorted([f for f in os.listdir(folder) if f.endswith(".md") or f.endswith(".txt")])

def export_people_to_markdown(people,roles):
    """Export the list of people if they are available for a role to a Markdown string."""
    markdown_text = []
    # Write the title
    markdown_text.append(f"\n# List of ministers\n")
    # Iterate over the roles
    for role in roles:
        markdown_text.append(f"## {role.name}\n")
        # List the people available for the role
        # each person gets a bullet point with their name and surname, phone number, and email
        for person in people:
            if role.name in person.roles:
                print("DEBUG: ", person.name, person.surname, person.phone, person.email)
                markdown_text.append(f"- {person.name} {person.surname}, {person.phone}, {person.email}")
        markdown_text.append("\n")
    markdown_text.append("\n---\n")

    return "\n".join(markdown_text)