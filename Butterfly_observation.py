

class Butterfly_observation:

    def __init__(self, species, amount, north_coordinate, date):
        self.species = species
        self.amount = amount
        self.north_coordinate = north_coordinate
        self.date = date

    def __repr__(self):
        return f"{self.species} {self.amount} {self.north_coordinate} {self.date}"
    


    




