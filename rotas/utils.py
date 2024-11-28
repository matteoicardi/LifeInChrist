import subprocess
import os

def export_to_markdown(rota, date_range, duty_count, duty):
    """
    Export the rota to a Markdown string.

    Parameters:
        rota (list): A list of mass schedules, each a dictionary with date, mass_day, and roles.
        date_range (str): The date range for the rota.
        duty_count (dict): A dictionary with person names and role name as keys, counting the number of duties.
        duty (dict): A dictionary with person names and role name as keys, listing the dates of duties.

    Returns:
        str: The Markdown content as a string.
    """
    markdown_text = []

    # Write the title
    markdown_text.append(f"# Rota {date_range}\n")

    # Iterate over the masses in the rota
    for entry in rota:
        mass_day = entry["mass_day"]
        date = entry["date"].strftime("%A, %d %B %Y")  # Format date as "Day, DD Month YYYY"
        week_number = entry["week_number"]

        markdown_text.append(f"### {date}, Week {week_number}\n")
        
        # Write roles and their assignments
        for role, people in entry["roles"].items():
            #list people names only for elements of assigned_people that are not None
            assigned_people = [p for p in people if p is not None]
            print(assigned_people)
            people_names = ", ".join([f"{p.name} {p.surname}" for p in assigned_people])
            markdown_text.append(f"- **{role}:** {people_names if people_names else 'No assignment'}")
            # Add the remaining Unassigned tasks
            if len(assigned_people) < len(people):
                unassigned = len(people) - len(assigned_people)
                markdown_text.append(unassigned * ", Unassigned")
            markdown_text.append("\n")

        markdown_text.append("\n")  # Separate masses
    
    
    # Add a section for duties listing the number of duties each person has
    markdown_text.append(f"\n# List of duties {date_range}\n")
    # duties is a dictionary with person names and role name as keys
    for person in duty_count:
        markdown_text.append(f"### {person}\n")
        for role in duty_count[person]:
            markdown_text.append(f"- {role}: {duty_count[person][role]} (")
            for date in duty[person][role]:
                markdown_text.append(f" {date.strftime('%d %B %Y')},")
            markdown_text.append(")\n")
        markdown_text.append("\n")       

    # Add a footer
    markdown_text.append("\n---\nGenerated automatically by MI's rota program.\n")

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
