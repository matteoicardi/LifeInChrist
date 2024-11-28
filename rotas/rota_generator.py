from datetime import timedelta
import random

def generate_rota(people, roles, weekends):
    """
    Generate a rota based on people, role requirements, and weekends, with considerations for 'with:' preferences and equitable assignments.

    Parameters:
        people (list): List of Person objects.
        roles (list): List of Role objects.
        weekends (list): List of tuples (mass_day, week_number, date).
        is_unavailable (function): Function to check if a person is unavailable for a specific mass day.

    Returns:
        list: A rota as a list of dictionaries, where each dictionary represents the schedule for a specific mass.
    """
    rota = []  # List to hold the schedule for each mass
    duty_count = {person.name: {role.name: 0 for role in roles} for person in people}  # Track the number of duties per person per role
    duty = {person.name: {role.name: [] for role in roles} for person in people}  # Track the dates of duties per person per role
    random.seed(42)  # Seed the random number generator for reproducibility

    weekend_people = []
    week_number0 = -1

    for mass_day, week_number, date in weekends:
        mass_schedule = {"date": date, "mass_day": mass_day, "week_number": week_number, "roles": {}}
        if week_number != week_number0:
            weekend_people = []
            week_number0 = week_number

        # Track the with_person preference for those already assigned
        assigned_with_preference = set()
        
        for role in roles:
            # Determine the number of people required for this role at this mass
            required = getattr(role, f"{mass_day.lower()}_required", 0)

            # Filter people who are available for this mass, this role, and this week
            available_people = [
                person
                for person in people
                if mass_day in person.masses # Check mass day
                and role.name in person.roles # Check role
                and not is_unavailable(person, mass_day, week_number, date) # Check availability
                and person not in weekend_people  # avoid more roles in a weekend
            ]
            
            # Sort people by their duty count for this specific role (minimizing assigned duties)
            available_people.sort(key=lambda p: duty_count[p.name].get(role.name, 0))
                                
            # List to track selected people for the current role
            selected_people = []
            
            # First add those who are both in the free_people list and in the assigned_with_preference set up to a limit of required
            while len(selected_people) < required:
                if not available_people:
                    print(f"Warning: Not enough people available for {role.name} on {date} ({mass_day}), week {week_number}")
                    break
                # Count the minimum duty count for the available people
                min_duty_count = min(duty_count[p.name][role.name] for p in available_people)
                # Create a list of people with the minimum duty count
                free_people = [p for p in available_people if duty_count[p.name][role.name] == min_duty_count]
                in_both_sets = [p for p in free_people if p.name in assigned_with_preference]
                # create a list to_add first with the free with preferences and then with the first free
                to_add = in_both_sets[:required - len(selected_people)]
                selected_people.extend(to_add)
                for person in to_add:
                    duty_count[person.name][role.name] += 1
                    duty[person.name][role.name].append(date)
                    assigned_with_preference.update(person.with_person)
                # update available_people to remove the selected people
                available_people = [p for p in available_people if p not in to_add]
                # Sort people by their duty count for this specific role (minimizing assigned duties)
                available_people.sort(key=lambda p: duty_count[p.name].get(role.name, 0))
                if len(selected_people) >= required:
                    break
                else:
                    if not available_people:
                        print(f"Warning: Not enough people available for {role.name} on {date} ({mass_day}), week {week_number}")
                        break
                    # add the first person in the available_people list
                    selected_people.append(available_people.pop(0))
                    duty_count[selected_people[-1].name][role.name] += 1
                    duty[selected_people[-1].name][role.name].append(date)
                    assigned_with_preference.update(selected_people[-1].with_person)
                    
            # Add the role assignment to the mass schedule
            mass_schedule["roles"][role.name] = selected_people
            weekend_people.extend(selected_people)

        rota.append(mass_schedule)

    return rota, duty_count, duty

def is_unavailable(person, mass_day, week_number, date):
    """
    Check if a person is unavailable for a given mass, week number, or specific date.

    Parameters:
        person (Person): The person to check.
        mass_day (str): "Sat" or "Sun".
        week_number (int): The number of the week (1-based).
        date (datetime): The date of the mass.

    Returns:
        bool: True if the person is unavailable, False otherwise.
    """
    
    # # Debug
    # print(f"Checking availability for {person.name} {person.surname} on {date} ({mass_day}), week {week_number}")
    
    # Check AvoidWeeks
    if week_number in person.avoid_weeks:
        return True
    
    # Check Masses
    if mass_day not in person.masses:
        return True

    # Check AvoidDates
    for start_date, end_date in person.avoid_dates:
        if start_date <= date <= end_date:
            return True

    return False

def compute_weekends(start_date, end_date):
    """
    Compute all Saturdays and Sundays within a given date range and assign week numbers based on the month.

    Parameters:
        start_date (datetime): The start of the date range.
        end_date (datetime): The end of the date range.

    Returns:
        list: List of (mass_day, week_number, mass_date) tuples, where mass_day is "Sat" or "Sun".
    """
    weekends = []
    current_date = start_date

    # Find the first Sunday
    while current_date.weekday() != 6:  # 6 = Sunday
        current_date += timedelta(days=1)

    current_month = current_date.month  # Start with the first month in the range

    while current_date <= end_date:
        # Calculate the week number for the current day of the month
        week_number = (current_date.day - 1) // 7 + 1

        # Add the Saturday before the Sunday
        saturday = current_date - timedelta(days=1)
        if saturday >= start_date:
            weekends.append(("Sat", week_number, saturday))

        # Add the Sunday
        if current_date >= start_date:
            weekends.append(("Sun", week_number, current_date))

        # Move to the next week
        current_date += timedelta(days=7)

    return weekends