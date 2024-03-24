from biosim.animals import Herbivores, Carnivores


class Cells:
    """
    Class Cells:

    Superclass with common methods for all of the landscapes
    =============================================================
    **is mainland:** if the cell is mainland the animal can move to the cell

    **sort the herbivore population by fitness:** sort herbivore list from least fit to most fit

    **add animals:** adds animals to a population count

    **animals number:** counts amount of animals in the population count

    **annual animals weight loss and aging:** update values for age and weight

    **migrating:** sets animal into their cell

    **regrowth:** fodder amount for the herbivores

    **herbivore feeding:** herbivores eating the available fodder based on appetite

    **animal death:** if animal is dead remove dead animal

    **carnivores eat:** if herbivore is in the same cell as a herbivore it will eat
    herbivores to fulfill its appetite

    **add newborns:** adds new animals to the population

    **kill all animals:** checks if animal is alive

    **yearly cycle till migration:** functions will happen yearly and does not rely on migration

    **yearly cycle after migration:** yearly cycles relying on migration
    """
    parameters: dict

    @property
    def is_mainland(self):
        """
        :return: if landscape is mainland
        :rtype: bool
        """
        return True

    @classmethod
    def set_parameters(cls, params):
        for key in params:
            if key not in cls.parameters:
                raise KeyError(key, "is not a valid parameter for the animal")
            elif params[key] < 0:
                raise ValueError("Value for the parameter", key, "should be positive integer")
            else:
                cls.parameters[key] = params[key]

    def __init__(self):
        """
        Constructor
        -----------
        contains data for later use
        """
        self.animal_population = {'Herbivores': [], 'Carnivores': []}
        self.total_population = None
        self.cell_neighbors = []
        self.has_moved = False
        self.amount_fodder = None

    def sort_herbivores_population_by_fitness(self, species, descending=True):
        """
        sort herbivore list by their fitness descending

        :param species: which species
        :type species: string

        :param descending: sort list in dict in descending order
        :type descending: bool
        """

        self.animal_population[species] = sorted(self.animal_population[species], key=lambda x: x.fitness,
                                                 reverse=descending)

    def add_animals(self, population=None):
        """
        adds the individual animals age and weight to the species population list

        :param population: count population
        :type population: list
        """

        for animal in population:
            if animal['species'] == 'Herbivore':
                self.animal_population['Herbivores'].append(Herbivores(animal['age'], animal['weight']))
            if animal['species'] == 'Carnivore':
                self.animal_population['Carnivores'].append(Carnivores(animal['age'], animal['weight']))

    def animals_num(self):
        """
        length of the species population list

        :return: number of given species
        :rtype: tuple
        """
        return len(self.animal_population['Herbivores']), len(self.animal_population['Carnivores'])

    def annual_animals_weight_loss_and_aging(self):
        """
        updates the annual weight loss and aging
        """
        for animal in self.animal_population['Herbivores'] + self.animal_population['Carnivores']:
            animal.animal_aging()
            animal.weight_loss()

    def migrating(self):
        """
        Add migrated animals in to their new cell
        """
        self.migrated_animals = []
        for animal in self.animal_population['Herbivores'] + self.animal_population['Carnivores']:
            if animal.migrating():
                self.migrated_animals.append(animal)
            # if len(self.cell_neighbors) > 0:
            #     chosen_cell = random.choice(self.cell_neighbors)
            #     chosen_cell.add_animals([animal])
            #     migrated_animals.append(animal)

    def regrowth(self):
        """
        Sets amount of fodder for herbivores to maximum.
        """
        self.amount_fodder = self.parameters['f_max']

    def herbivore_feeding(self):
        """
        This method returns the amount of fodder available to a Herbivore. If a lot
        of fodder is available in the cell, enough fodder will be return to fulfill it's
        appetite F. if not, whats left will be returned.
        """

        self.sort_herbivores_population_by_fitness("Herbivores")
        for herbivore in self.animal_population["Herbivores"]:
            appetite_herbivores = Herbivores.parameters['F']

            if self.amount_fodder >= appetite_herbivores:
                self.amount_fodder -= appetite_herbivores
                herbivore.weight_gain(appetite_herbivores)

            elif 0 < self.amount_fodder < appetite_herbivores:
                herbivore.weight_gain(self.amount_fodder)
                self.amount_fodder = 0
            else:
                break

    def animal_death(self):
        """
        function for animal death
        """
        def remove_animal(animals):
            """
            if an animal is dead it must be removed

            :param animals: individual animal
            :type animals: list

            :return: remove dead animal from count
            :rtype: list
            """
            return [animal for animal in animals if not animal.death()]

        self.animal_population['Herbivores'] = remove_animal(self.animal_population['Herbivores'])
        self.animal_population['Carnivores'] = remove_animal(self.animal_population['Carnivores'])

    def carnivores_eat(self):
        """
        Carnivores eat in order of highest fitness. The Carnivore tries to
        kill the Herbivore with lowest fitness first. The Carnivore's weight
        increases.
        """
        self.sort_herbivores_population_by_fitness('Herbivores', False)
        for carnivores in self.animal_population['Carnivores']:
            food_eaten = 0
            killed_herbivores = []
            for herbivores in self.animal_population['Herbivores']:
                food = 0
                if food_eaten < carnivores.parameters['F']:
                    if carnivores.killing(herbivores.fitness):
                        killed_herbivores.append(herbivores)
                        weight_prey = herbivores.weight
                        if food_eaten + weight_prey > carnivores.parameters['F']:
                            food = carnivores.parameters['F'] - food_eaten
                            food_eaten = carnivores.parameters['F']
                        else:
                            food = weight_prey
                            food_eaten += weight_prey
                        carnivores.weight_gain(food)
            self.animal_population['Herbivores'] = [herb for herb in self.animal_population['Herbivores'] if
                                                    herb not in killed_herbivores]

    def add_newborn_animal(self):
        """
        Adds newborn animals to the list

        *Is done for both herbivore and carnivore*
        """
        newborn_animal = []
        n = self.animals_num()

        for herbivore in self.animal_population['Herbivores']:
            newborn = herbivore.birth(n[0])
            if newborn is not None:
                newborn_animal.append(newborn)
        self.animal_population['Herbivores'] += newborn_animal

        newborn_animal = []
        for carnivore in self.animal_population['Carnivores']:
            newborn = carnivore.birth(n[1])
            if newborn is not None:
                newborn_animal.append(newborn)
        self.animal_population['Carnivores'] += newborn_animal

    def kill_all_animals(self):
        """
        Checks if the animals are alive, if alive it is kept in the list

        *Is done for both herbivore and carnivore*
        """
        alive_herbivores = []
        for herbivore in self.animal_population['Herbivores']:
            if herbivore.alive is True:
                alive_herbivores.append(herbivore)
        self.animal_population['Herbivores'] = alive_herbivores

        alive_carnivores = []
        for carnivore in self.animal_population['Carnivore']:
            if carnivore.alive is True:
                alive_carnivores.append(carnivore)
        self.animal_population['Carnivore'] = alive_carnivores

    def yearly_cycle_till_migration(self):
        """
        Every cycle these functions is updated
        """

        self.regrowth()
        self.herbivore_feeding()
        self.carnivores_eat()
        self.add_newborn_animal()
        self.migrating()

    def yearly_cycle_after_migration(self):
        """
        Functions relying on migration that happens every cycle
        """
        self.annual_animals_weight_loss_and_aging()
        self.animal_death()


class Lowland(Cells):
    """
    Subclass containing the parameters for the lowland cells
    """
    parameters = {'f_max': 800.0}


class Highland(Cells):
    """
    Subclass containing the parameters for the highland cells
    """
    parameters = {'f_max': 300.0}


class Desert(Cells):
    """
    Subclass containing the parameters for the desert cells
    """
    parameters = {'f_max': 0.0}


class Water(Cells):
    """
    Subclass for the water cells
    """
    @property
    def is_mainland(self):
        """
        :return: checks if cell is mainland
        :rtype: bool
        """
        return False



