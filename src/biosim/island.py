from .cells import Lowland, Highland, Desert, Water
import random
import numpy as np

class Rossumoya:
    """
    .

    Class for the island Rossumoya:
    ===============================
    **map from string:** reads the string containing the map

    **addition of population:** how many animals in the different locations

    **count animals:** count animals in the list

    **delete animals:** deletes animals from counter

    **numbers of animal:** the total amount of animals

    **numbers of herbivores:** the total amount of herbivores

    **numbers of carnivores:** the total amount of carnivores

    **movement of migrating animals:** to which cells a migrating animal can move

    **simulation cycle:** the yearly cycle for the simulation
    """

    def __init__(self, geogr_str):
        """
        Constructor
        ------------
        contains data for later use

        :param geogr_str: a string with the geography of the island
        :type geogr_str: str
        """
        self.cells = self.map_from_str(geogr_str)
        self.geogr_str = geogr_str

        self.num_herbivores = 0
        self.num_carnivores = 0

    @staticmethod
    def map_from_str(geogr_str):
        """
        :param geogr_str: information from a string about the map
        :type geogr_str: str
        :return: a map where each letter symbolize a landscape
        :rtype: dict

        :raise ValueError: Invalid boundary

        :raise ValueError: Map string must be W, L, H or D
        """
        map_dict = {}

        row_length = [len(row.strip()) for row in geogr_str.strip(' ').splitlines()]
        for i, row in enumerate(row_length[:-1]):
            if row_length[i] != row_length[i + 1]:
                raise ValueError('Map needs uniform row length')
        lines = geogr_str.strip(' ').splitlines()
        for char in lines[0] + lines[-1]:
            if char != "W":
                raise ValueError("Invalid boundary")
        for line in lines:
            if line[0] != "W" and line[-1] != "W":
                raise ValueError("Invalid boundary")
        for row_coord, cell_row in enumerate(geogr_str.splitlines()):
            for col_coord, cell in enumerate(cell_row.strip()):
                coord = (row_coord + 1, col_coord + 1)

                if cell == 'W':
                    map_dict[coord] = Water()
                elif cell == 'L':
                    map_dict[coord] = Lowland()
                elif cell == 'H':
                    map_dict[coord] = Highland()
                elif cell == 'D':
                    map_dict[coord] = Desert()
                else:
                    raise ValueError("Map string must be W, L, H or D")
        return map_dict

    def addition_of_population(self, pop):
        """
        population in the location

        :param pop: population of the species
        :type pop: list
        """
        for entries in pop:
            self.cells[entries['loc']].add_animals(entries['pop'])

    def count_animals(self, num_herbs=0, num_carns=0, animal_list=None):
        """
        count animals in lists

        :param num_herbs: numbers of herbivores
        :type num_herbs: int

        :param num_carns: number of carnivores
        :type num_carns: int

        :param animal_list: number of animals (*herbivores + carnivores*)
        :type animal_list: int

        :raise ValueError: must be a positive integer
        """
        if num_herbs >= 0 and num_carns >= 0:
            self.num_herbivores += num_herbs
            self.num_carnivores += num_carns
        else:
            raise ValueError('must be a positive integer')

        if animal_list is not None:
            self.num_herbivores += len([animal for animal in animal_list if animal.species == 'Herbivore'])
            self.num_carnivores += len([animal for animal in animal_list if animal.species == 'Carnivore'])

    def delete_animals(self, num_herbs=0, num_carns=0, animal_list=None):
        """
        deletes animals from the counter

        :param num_herbs: numbers of herbivores
        :type num_herbs: int

        :param num_carns: number of carnivores
        :type num_carns: int

        :param animal_list:number of animals (*herbivores + carnivores*)
        :type animal_list: list

        :raise ValueError: must be a positive integer
        """
        if num_herbs >= 0 and num_carns >= 0:
            self.num_herbivores -= num_herbs
            self.num_carnivores -= num_carns
        else:
            raise ValueError('must be a positive integer')

        if animal_list is not None:
            self.num_herbivores -= len([animal for animal in animal_list if animal.species == 'Herbivore'])
            self.num_carnivores -= len([animal for animal in animal_list if animal.species == 'Carnivore'])

    def carnivores_matrix(self):
        """
        Makes matrix for carnivores

        :return: a matrix for the carnivores
        """

        lines = self.geogr_str.splitlines()
        dim = (len(lines), len(lines[0]))
        matrix_carn = np.zeros(dim)
        for loc, cells in self.cells.items():
            if not cells.is_mainland:
                continue
            matrix_carn[loc[0] - 1][loc[1] - 1] = len(cells.animal_population['Carnivores'])
        return matrix_carn

    def herbivores_matrix(self):
        """
        Makes matrix for herbivores
        :return: a matrix for the herbivores

        """
        lines = self.geogr_str.splitlines()
        dim = (len(lines), len(lines[0]))
        matrix_herb = np.zeros(dim)
        for loc, cells in self.cells.items():
            if not cells.is_mainland:
                continue
            matrix_herb[loc[0] - 1][loc[1] - 1] = len(cells.animal_population['Herbivores'])
        return matrix_herb

    def herb_hist_lists(self):
        """
        Histogram for herbivores
        :return: histogram containing fitness, age and weight
        :rtype: list
        """
        h_lists = {"fit": [], "age": [], "wt": []}
        for cell in self.cells.values():
            if not cell.is_mainland:
                continue
            for herbs in cell.animal_population["Herbivores"]:
                h_lists["fit"].append(herbs.fitness)
                h_lists["age"].append(herbs.age)
                h_lists["wt"].append(herbs.weight)
        return h_lists

    def carn_hist_lists(self):
        """
        Histogram for carnivores
        :return: histogram containing fitness, age and weight
        :rtype: list
        """
        c_lists = {"fit": [], "age": [], "wt": []}
        for cell in self.cells.values():
            if not cell.is_mainland:
                continue
            for carn in cell.animal_population["Carnivores"]:
                c_lists["fit"].append(carn.fitness)
                c_lists["age"].append(carn.age)
                c_lists["wt"].append(carn.weight)
        return c_lists

    @property
    def numb_animals(self):
        """
        :return: total amount of animals
        :rtype: int
        """
        return self.num_herbivores + self.num_carnivores

    @property
    def numb_herbs(self):
        """
        :return: total amount of herbivores
        :rtype: int
        """
        return self.num_herbivores

    @property
    def numb_carns(self):
        """
        :return: total amount of carnivores
        :rtype: int
        """
        return self.num_carnivores

    def movement_of_migrating_animals(self):
        """
        An animal within a cell can move one step to its neighbor cells (*but not diagonally*)

        It choose to do so randomly

        :raise AttributeError: Somewhere the species has been changed
        """
        for loc, cell in self.cells.items():
            if not cell.is_mainland:
                continue
            else:
                directions = [(loc[0] + 1, loc[1]), (loc[0], loc[1] - 1), (loc[0], loc[1] + 1), (loc[0] - 1, loc[1])]
                for animal in cell.migrated_animals:
                    moving_direction = random.choice(directions)
                    if not self.cells[moving_direction].is_mainland:
                        continue
                    else:
                        if animal.species == 'Herbivore':
                            self.cells[moving_direction].animal_population['Herbivores'].append(animal)
                            self.cells[loc].animal_population['Herbivores'].remove(animal)
                        elif animal.species == 'Carnivore':
                            self.cells[moving_direction].animal_population['Carnivores'].append(animal)
                            self.cells[loc].animal_population['Carnivores'].remove(animal)

                        else:
                            raise AttributeError("Somewhere the species has been changed")

    def simulation_cycle(self):
        """
        The animals can migrate on the island one time a year
        """
        for loc, cell in self.cells.items():
            if not cell.is_mainland:
                continue
            else:
                cell.yearly_cycle_till_migration()

        self.movement_of_migrating_animals()

        for loc, cell in self.cells.items():
            if not cell.is_mainland:
                continue
            else:
                cell.yearly_cycle_after_migration()
