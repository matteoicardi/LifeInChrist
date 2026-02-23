from parsers import read_people, read_roles
from rota_generator import generate_rota, compute_weekends, compute_special_dates
from utils import export_to_markdown, convert_md_to_pdf, generate_filename, write_file, export_people_to_markdown
from datetime import datetime
import argparse
import os
import markdown


def main():
    parser = argparse.ArgumentParser(description="Generate a parish rota.")
    parser.add_argument(
        "date_range",
        type=str,
        help="Date range for the rota in the format DD/MM/YYYY-DD/MM/YYYY",
    )
    parser.add_argument(
        "roles",
        nargs='*',
        help="Optional list of roles to include in the rota",
    )
    parser.add_argument(
        "--add-contacts",
        action="store_true",
        help="Append contacts for ministers to the generated Markdown",
    )
    args = parser.parse_args()

    # Parse the date range
    try:
        start_str, end_str = args.date_range.split("-")
        start_date = datetime.strptime(start_str.strip(), "%d/%m/%Y")
        end_date = datetime.strptime(end_str.strip(), "%d/%m/%Y")
    except ValueError:
        print("Error: Invalid date range format. Use DD/MM/YYYY-DD/MM/YYYY.")
        return 1

    # Compute weekends and special dates
    weekends = compute_weekends(start_date, end_date)
    roles_folder = "data/roles"
    roles = read_roles(roles_folder)
    # add special dates from roles (if any)
    weekends.extend(compute_special_dates(start_date, end_date, roles))
    weekends.sort(key=lambda x: x[2])

    # Load people and roles
    people_folder = "data/people"
    people = read_people(people_folder)

    # Filter roles if specified on CLI
    if args.roles:
        roles = [role for role in roles if role.name in args.roles]

    if not roles:
        print("Error: No roles found. Check the roles folder or spell the roles correctly as argument of the function.")
        return 1

    # Filter people for selected roles
    people = [person for person in people if any(role.name in person.roles for role in roles)]

    # Generate the rota
    rota, duty_count, duty = generate_rota(people, roles, weekends)

    # Generate filename and ensure output folder exists
    output_filename = generate_filename(start_date, end_date)
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    # Export the rota to Markdown
    markdown_text = export_to_markdown(rota, args.date_range, duty_count, duty)
    if args.add_contacts:
        markdown_text += export_people_to_markdown(people, roles)

    write_file(output_filename, markdown_text)
    print(f"Rota successfully exported to {output_filename}")

    # Export HTML
    output_html_filename = output_filename.replace('.md', '.html')
    html_text = markdown.markdown(markdown_text)
    write_file(output_html_filename, html_text)
    print(f"HTML successfully generated: {output_html_filename}")

    # Convert the generated Markdown file to PDF
    output_pdf_filename = output_filename.replace('.md', '.pdf')
    try:
        convert_md_to_pdf(output_filename, output_pdf_filename)
        print(f"PDF successfully generated: {output_pdf_filename}")
    except Exception as e:
        print(f"Error generating PDF: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())