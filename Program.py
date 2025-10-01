from Butterfly_observation import Butterfly_observation
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

def read_data(filename, butterflies):

    with open(filename, encoding="utf-8", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')

        next(reader) # Skip header row

        for row in reader:
            try:
                species = row[6].replace("[", "").replace("]", "").strip().capitalize() # Some data has brackets, e.g. [species] --> species
                
                if row[9] == "noterad":
                    amount = 1 # per instructions
                elif row[9].isdigit():
                    amount = int(row[9])
                else:
                    amount = 0 # if empty or "onoterad"
            
                north_coordinate = int(row[20])
                date = datetime.strptime(row[30], "%Y-%m-%d") # save date as datetime object

            except (IndexError, ValueError) as e:
                print(f"Skipping row: {e}")
                continue
            
            if species not in butterflies:
                butterflies[species] = []

            butterflies[species].append(Butterfly_observation(species, amount, north_coordinate, date))

    return butterflies

def plot_spread(butterflies, species_name):
    """
    This function plots the northernmost observation of a butterfly species over the years.
    It prompts the user for a species name and then generates a line plot showing the northernmost observation for that species from 2002 to 2022.

    Parameters:
    butterflies (dict): A dictionary where keys are species names and values are lists of Butterfly_observation objects.
    species_name (str): The name of the butterfly species to plot.

    Returns:
    None: Displays a plot of the northernmost observations for the specified species.
    """

    if species_name not in butterflies:
        print(f"Species {species_name} not found in the data.")
        return
    
    observations = butterflies[species_name]

    yearly_max_north_coordinate = {}

    for obs in observations:
 
        try:
            year = obs.date.year 
            north_coordinate = int(obs.north_coordinate)
        except ValueError as e:
            print(f"Skipping observation: {e}")
            continue

        if year not in yearly_max_north_coordinate or north_coordinate > yearly_max_north_coordinate[year]:
            yearly_max_north_coordinate[year] = north_coordinate
    
    years = sorted(yearly_max_north_coordinate.keys())
    max_lats = [yearly_max_north_coordinate[year] for year in years]

    # coordinates according to RT 90
    ystad_north_coordinate = 6164000
    abisko_north_coordinate = 7585000 

    plt.figure(figsize=(10, 6))
    plt.plot(years, max_lats, marker='o', label='Nordligaste observation')

    plt.axhline(ystad_north_coordinate, color='red', linestyle='--')
    plt.axhline(abisko_north_coordinate, color='red', linestyle='--')

    left_year = years[0]
    plt.text(left_year, ystad_north_coordinate + 10000, 'Ystad', color='black', fontsize=10, ha='left', va='bottom')
    plt.text(left_year, abisko_north_coordinate + 10000, 'Abisko', color='black', fontsize=10, ha='left', va='bottom')

    plt.title(f"{species_name}: northernmost observation")
    plt.xlabel('Year')
    plt.ylabel('Latitude (RT 90)')
    plt.grid(False)
    full_years =list(range(2002, 2023))
    plt.xticks(full_years[::2], [str(y) for y in full_years[::2]]) 

    filename = f"{species_name}_northernmost_observation.pdf"
    plt.savefig(filename, format="pdf", bbox_inches='tight')
    print(f"Plot saved as {filename}")

    plt.close() # close figure to free memory


def plot_observations(butterflies, species_name):
    """
    This function plots the number of observations per year for a given butterfly species.
    It prompts the user for a species name and then generates a line plot showing the number of observations for each year from 2002 to 2022.

    Parameters:
    butterflies (dict): A dictionary where keys are species names and values are lists of Butterfly_observation objects.
    species_name (str): The name of the butterfly species to plot.
    
    Returns:
    None: Displays a plot of observations per year for the specified species.
    """

    yearly_amount = {}

    for species, observations in butterflies.items():
        if species != species_name:
            continue

        for obs in observations:
            try:
                year = obs.date.year
            except ValueError:
                continue

            if 2002 <= year <= 2022:
                yearly_amount[year] = yearly_amount.get(year, 0) + 1
    
    if not yearly_amount:
        print(f"No observations found for species {species_name}.")
        return
    
    years = list(range(2002, 2023))
    amounts = [int(yearly_amount.get(year, 0)) for year in years]

    plt.figure(figsize=(10, 6))
    plt.plot(years, amounts, marker='o', color='blue')
    plt.xticks(years[::2], [str(y) for y in years[::2]]) 
    plt.title(f"{species_name}: observerations per year")
    plt.xlabel('Year')
    plt.ylabel('# observations')
    plt.grid(False)
    
    filename = f"{species_name}_observations_per_year.pdf"
    plt.savefig(filename, format="pdf", bbox_inches='tight')
    print(f"Plot saved as {filename}")

    plt.close()  # close figure to free memory


def plot_activity(butterflies, species_name):
    """
    This function plots the weekly activity of a butterfly species for a given year.    
    It prompts the user for a species name and a year, then calculates the number of observations per week for that species in the specified year.

    Parameters:
    butterflies (dict): A dictionary where keys are species names and values are lists of Butterfly_observation objects.
    species_name (str): The name of the butterfly species to plot.

    Returns:
    None: Displays a bar plot of weekly observations for the specified species and year.

    """

    try: 
        requested_year = int(input("Enter the year (e.g., 2022): "))
    except ValueError:
        print("Invalid year.")
        return

    if species_name not in butterflies:
        print(f"Species {species_name} not found in the data.")
        return
    
    observations_per_week = {}

    for obs in butterflies[species_name]:
        try:
            date = obs.date
        except ValueError:
            continue

        if date.year != requested_year:
            continue

        week_number = date.isocalendar()[1]  # weeknr 1-52
        observations_per_week[week_number] = observations_per_week.get(week_number, 0) + 1

    if not observations_per_week:
        print(f"No observations found for species {species_name} in {requested_year}.")
        return
            
    weeks = list(range(1, 53))
    amounts = [observations_per_week.get(week, 0) for week in weeks]

    total_observations = sum(amounts)
    percentages = [(amount / total_observations) * 100 for amount in amounts]

    cumulative = []
    running_sum = 0
    for amount in amounts:
        running_sum += amount
        cumulative.append(running_sum / total_observations * 100)

    start_week = None
    end_week = None
    for week, cumul in zip(weeks, cumulative):
        if start_week is None and cumul >= 5:
            start_week = week
        if end_week is None and cumul >= 95:
            end_week = week
            break

    fractions = [amount / total_observations for amount in amounts]

    max_fraction = max(fractions)
    yticks = np.arange(0, max_fraction + 0.01, 0.025)

    plt.figure(figsize=(10, 6))
    plt.bar(weeks, fractions, color='grey', edgecolor='black')

    if start_week and end_week:
        for week in range(start_week, end_week + 1):
            plt.bar(week, fractions[week - 1], color='blue', edgecolor='black')

    plt.xlabel('Week number')
    plt.ylabel('observations')
    plt.title(f"{species_name}: weekly observations {requested_year}")
    plt.xticks(range(0, 53, 10))
    plt.yticks(yticks)
    plt.ylim(0, max_fraction * 1.1)
    plt.grid(False)
    
    filename = f"{species_name}_weekly_activity_{requested_year}.pdf"
    plt.savefig(filename, format="pdf", bbox_inches='tight')
    print(f"Plot saved as {filename}")

    plt.close()  # close figure to free memory


if __name__ == "__main__":
    running = True

    while True:
            data_folder_name = "butterfly_data"

            folder = Path(data_folder_name)
            if folder.is_dir():
                break
            else:
                print("Error: folder not found, try again!")

    butterflies = {}

    for csv_file in folder.glob("*.csv"):
        print(f"Processing file: {csv_file.name}")
        read_data(csv_file, butterflies)

    for species, observations in butterflies.items():
        total_amount = sum(int(obs.amount) for obs in observations)
        print(f"{species}: {total_amount} observations")

    while running:

        while True:
            plot_choice = input("Choose a plot type: (1) Spread, (2) Observations, (3) Activity: ")
            if plot_choice in ['1', '2', '3']:
                break
            else:
                print("Invalid choice, please try again.")
            
        while True:
            species_choice = input("Enter species name: ").strip().capitalize()
            if species_choice in butterflies:
                break
            else:
                print(f"Species {species_choice} not found, please try again.")

        if plot_choice == '1':
            plot_spread(butterflies, species_choice)    
        elif plot_choice == '2':
            plot_observations(butterflies, species_choice)
        elif plot_choice == '3':
            plot_activity(butterflies, species_choice)

        again_choice =input("Do you want to continute? y/n: ").lower()
        if again_choice != 'y':
            running = False
            print("Exiting the program.")
        

    



    




