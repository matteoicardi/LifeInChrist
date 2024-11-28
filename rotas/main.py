from parsers import read_people, read_roles
from rota_generator import generate_rota, compute_weekends
from utils import export_to_markdown, convert_md_to_pdf, generate_filename
from datetime import datetime
import argparse


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate a parish rota.")
    parser.add_argument(
        "date_range",
        type=str,
        help="Date range for the rota in the format DD/MM/YYYY-DD/MM/YYYY",
    )
    args = parser.parse_args()

    # Parse the date range
    try:
        start_str, end_str = args.date_range.split("-")
        start_date = datetime.strptime(start_str.strip(), "%d/%m/%Y")
        end_date = datetime.strptime(end_str.strip(), "%d/%m/%Y")
    except ValueError:
        print("Error: Invalid date range format. Use DD/MM/YYYY-DD/MM/YYYY.")
        exit(1)

    # Compute weekends
    weekends = compute_weekends(start_date, end_date)

    # Load people and roles
    people_folder = "data/people"
    roles_folder = "data/roles"

    people = read_people(people_folder)
    roles = read_roles(roles_folder)
    
    # Generate the rota
    rota,duty_count,duty = generate_rota(people, roles, weekends)

    # Generate filename based on the date range
    output_filename = generate_filename(start_date, end_date)

    # Export the rota to Markdown
    export_to_markdown(rota, output_filename, args.date_range, duty_count, duty)

    print(f"Rota successfully exported to {output_filename}")

    # Convert the generated Markdown file to PDF
    output_pdf_filename = output_filename.replace(".md", ".pdf")
    convert_md_to_pdf(output_filename, output_pdf_filename)

    print(f"PDF successfully generated: {output_pdf_filename}")   
