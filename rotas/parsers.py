import os
from datetime import datetime

class Person:
    def __init__(self, name, surname, phone, roles, masses, avoid_weeks, avoid_dates, with_person):
        self.name = name
        self.surname = surname
        self.phone = phone
        self.roles = roles
        self.masses = masses
        self.avoid_weeks = avoid_weeks
        self.avoid_dates = avoid_dates
        self.with_person = with_person

    def __repr__(self):
        return f"Person({self.name} {self.surname}, Phone: {self.phone}, Roles: {self.roles}, Masses: {self.masses}), AvoidWeeks: {self.avoid_weeks}, AvoidDates: {self.avoid_dates}, With: {self.with_person})"
    
    # write method to write the person object to a file
    def write(self, filepath):
        with open(filepath, 'w') as file:
            file.write(f"Name: {self.name}\n")
            file.write(f"Surname: {self.surname}\n")
            file.write(f"Phone: {self.phone}\n")
            file.write(f"Role: {', '.join(self.roles)}\n")
            file.write(f"Mass: {', '.join(self.masses)}\n")
            file.write(f"AvoidWeeks: {', '.join(self.avoid_weeks)}\n")
            file.write("AvoidDates: ")
            avoid_dates_str = ", ".join([f"{start_date.strftime('%d/%m/%Y')}-{end_date.strftime('%d/%m/%Y')}" for start_date, end_date in self.avoid_dates])
            file.write(avoid_dates_str + "\n")
            file.write(f"With: {', '.join(self.with_person)}\n")
    
    # read method to read the person object from a file
    @classmethod
    def read(cls, filepath):
        with open(filepath, 'r') as file:
            lines = file.readlines()

        data = {}
        for line in lines:
            key, value = line.strip().split(":", 1)
            key = key.strip()
            value = value.strip()
            if key in ["AvoidWeeks", "Mass", "Role", "With"]:
                data[key] = [v.strip() for v in value.split(",")]
            elif key == "AvoidDates":
                data[key] = parse_date_ranges(value)
            else:
                data[key] = value

        return cls(
            name=data["Name"],
            surname=data["Surname"],
            phone=data["Phone"],
            roles=data["Role"],
            masses=data["Mass"],
            avoid_weeks=data.get("AvoidWeeks", []),
            avoid_dates=data.get("AvoidDates", []),
            with_person=data.get("With", [])
        )
        # example of usage of this read method
        # person = Person.read(filepath)
    
        

class Role:
    def __init__(self, name, sat_required, sun_required, extra_dates):
        self.name = name
        self.sat_required = sat_required
        self.sun_required = sun_required
        self.extra_dates = extra_dates

    def __repr__(self):
        return f"Role({self.name}, Sat: {self.sat_required}, Sun: {self.sun_required}, Extra: {self.extra_dates})"
    
    # write method to write the role object to a file
    def write(self, filepath):
        with open(filepath, 'w') as file:
            file.write(f"Role: {self.name}\n")
            file.write(f"Sat: {self.sat_required}\n")
            file.write(f"Sun: {self.sun_required}\n")
            file.write("ExtraDates: ")
            extra_dates_str = ", ".join([f"{date.strftime('%d/%m/%Y')} ({num_people})" for date, num_people in self.extra_dates.items()])
            file.write(extra_dates_str + "\n")
                
                
    # read method to read the role object from a file
    @classmethod
    def read(cls, filepath):
        with open(filepath, 'r') as file:
            lines = file.readlines()

        data = {}
        for line in lines:
            key, value = line.strip().split(":", 1)
            key = key.strip()
            value = value.strip()
            if key in ["Sat", "Sun"]:
                data[key] = int(value)
            elif key == "ExtraDates":
                extra_dates = {}
                for extra_date in value.split(","):
                    date, num_people = extra_date.strip().split("(")
                    num_people = int(num_people.strip(")"))
                    extra_dates[datetime.strptime(date.strip(), "%d/%m/%Y")] = num_people
                data[key] = extra_dates
            else:
                data[key] = value

        return cls(
            name=data["Role"],
            sat_required=data["Sat"],
            sun_required=data["Sun"],
            extra_dates=data.get("ExtraDates", {})
        )
        # example of usage of this read method
        # role = Role.read(filepath)


def parse_date_ranges(dates_str):
    """Parse date ranges into tuples of datetime objects."""
    if not dates_str.strip():  # Check if the string is empty or contains only spaces
        return []
    date_ranges = []
    for date_range in dates_str.split(","):
        if "-" in date_range:
            start, end = date_range.strip().split("-")
            start_date = datetime.strptime(start, "%d/%m/%Y")
            end_date = datetime.strptime(end, "%d/%m/%Y")
            date_ranges.append((start_date, end_date))
        else:
            single_date = datetime.strptime(date_range.strip(), "%d/%m/%Y")
            date_ranges.append((single_date, single_date))
    return date_ranges


# read all people using the class method
def read_people(folder_path):
    """Load all people from the folder."""
    people = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".md") or filename.endswith(".txt"):
            print(f"Reading {filename}")
            filepath = os.path.join(folder_path, filename)
            people.append(Person.read(filepath))
    return people

# read all roles using the class method
def read_roles(folder_path):
    """Load all roles from the folder."""
    roles = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".md") or filename.endswith(".txt"):
            print(f"Reading {filename}")
            filepath = os.path.join(folder_path, filename)
            roles.append(Role.read(filepath))
    return roles

# save all people using the class method
def save_people(people, folder_path):
    """Save all people to the folder."""
    for person in people:
        filename = f"{person.name}_{person.surname}.txt"
        filepath = os.path.join(folder_path, filename)
        person.write(filepath)
        
# save all roles using the class method
def save_roles(roles, folder_path):
    """Save all roles to the folder."""
    for role in roles:
        filename = f"{role.name}.txt"
        filepath = os.path.join(folder_path, filename)
        role.write(filepath)
