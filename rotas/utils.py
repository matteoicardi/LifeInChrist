import subprocess
import os

def export_to_markdown(rota, output_file,date_range,duty_count,duty):
    """
    Export the rota to a Markdown file.

    Parameters:
        rota (list): A list of mass schedules, each a dictionary with date, mass_day, and roles.
        output_file (str): Path to the output Markdown file.
    """
    with open(output_file, "w") as file:
        # Write the title
        file.write(f"# All Saints West Nottingham, Rota {date_range}\n\n")

        # Iterate over the masses in the rota
        for entry in rota:
            mass_day = entry["mass_day"]
            date = entry["date"].strftime("%A, %d %B %Y")  # Format date as "Day, DD Month YYYY"
            week_number = entry["week_number"]

            file.write(f"### {date}, Week {week_number}\n")
            
            # Write roles and their assignments
            for role, assigned_people in entry["roles"].items():
                people_names = ", ".join([f"{p.name} {p.surname}" for p in assigned_people])
                file.write(f"- **{role}:** {people_names if people_names else 'No assignment'}\n")

            file.write("\n")  # Separate masses
        
        # Add a section for duties listing the number of duties each person has
        file.write("## List of duties\n")
        # duties is a dictionary with person names and role name as keys
        for person in duty_count:
            file.write(f"### {person}\n")
            for role in duty_count[person]:
                file.write(f"- {role}: {duty_count[person][role]} (")
                for date in duty[person][role]:
                    file.write(f" {date.strftime('%d %B %Y')},")
                file.write(")\n")
            file.write("\n")       
            

        # Add a footer
        file.write("\n---\nGenerated automatically by MI's rota program .\n")
        

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
    return [f for f in os.listdir(folder) if f.endswith(".md") or f.endswith(".txt")]
