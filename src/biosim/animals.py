import math  # math module to calculate equations
import random  # random module to collect random numbers


class Animals:
    """

    Class Animals:

    Superclass containing the common methods for subclasses
    ========================================================
    **animal aging:** animal gain age with one every cycle

    **calc birth weight:** animal is born with a 'unique' weight

    **weight gain:** if an animal eat it gains weight

    **weight loss:** yearly an animal lose a certain amount of weight

    **calc fitness:** determines the overall fitness of an animal

    **birth:** determines if a animal should give birth

    **migrating:** probability for an animal to migrate

    **death:** probability for an animal dying
    """
    parameters: dict

    @classmethod
    def set_parameters(cls, params):
        for key in params:
            if key not in cls.parameters:
                raise KeyError(key, "is not a valid parameter for the animal")
            elif params[key] < 0:
                raise ValueError("Value for the parameter", key, "should be positive integer")
            else:
                cls.parameters[key] = params[key]

    def __init__(self, age=None, weight=0):
        """
        Constructor
        -----------
        Contains data for later use

        :param age: Age of the animal
        :type age: int

        :param weight: Weight of the animal
        :type weight: float

        :raise ValueError: Age can not be negative
        :raise ValueError: Weight cannot be a negative integer
        """
        if age is None:
            age = 0
        self.age = int(age)
        if age < 0:
            raise ValueError('Age can not be negative')

        if weight == 0:
            weight = self.calc_birth_weight()
        self.weight = float(weight)

        if weight <= 0:
            raise ValueError('Weight cannot be a negative integer')
        self.fitness = 0
        self.calc_fitness()

    def animal_aging(self):
        """
        Age increases with 1 for each cycle that passes
        """
        self.age += 1

    def calc_birth_weight(self):
        r"""
        Calculates weight of an animal at birth

        **Formula for birth_weight**

        .. math::
            \begin{equation}
            w  \sim  GaussianDistribution \times (w_{birth}, \sigma_{birth})
            \end{equation}

        :return: Calculated birth weight drawn from a gaussian distribution
        :rtype: float
        """
        birth_weight = random.gauss(self.parameters['w_birth'], self.parameters['sigma_birth'])
        return birth_weight

    def weight_gain(self, food):
        r"""
        When eating, the animal gains weight

        *Change in weight must change the fitness*

        **Weight gain is given by the formula**

        .. math::
            \begin{equation}
            \beta \times F
            \end{equation}


        :param food: the amount of fodder an animal has eaten
        :type food: float
        """
        self.weight += self.parameters["beta"] * food
        self.calc_fitness()

    def weight_loss(self):
        r"""
        Each cycle the animal lose weight

        **Given by formula:**

        .. math::
            \begin{equation}
            \eta \times w
            \end{equation}

        *Change in weight must change the fitness*
        """
        self.weight -= (self.parameters['eta'] * self.weight)
        self.calc_fitness()

    def calc_fitness(self):
        r"""
        Fitness is the overall health of the animal

        Fitness is zero if weight is zero, otherwise given by

        **Calculates fitness based on age and weight**

        .. math::
            \begin{equation}
            q^{+} (a, a_{1/2}, phi_{age}) \times q^{-} (w, w_{1/2}, phi_{weight})
            \end{equation}

        where

        .. math::
            \begin{equation}
            q^{+-}(x, x_{1/2}, phi) = 1 / (1 + e^{{(+-)} \phi (x - x_{1/2})}
            \end{equation}
        """

        q_age = 1 / (1 + math.exp(self.parameters['phi_age'] * (self.age - self.parameters['a_half'])))
        q_weight = 1 / (1 + math.exp(-self.parameters['phi_weight'] * (self.weight - self.parameters['w_half'])))

        if self.weight <= 0:
            self.fitness = 0
        else:
            self.fitness = q_age * q_weight

    def migrating(self):
        r"""
        An animal can migrate to neighbor cells with a given probability

        **probability for migration**

        .. math::
            \begin{equation}
            \mu \times \Phi
            \end{equation}

        :return: The probability of an animal moving from one cell to an other
        :rtype: bool
        """
        move_probability = self.parameters['mu'] * self.fitness
        if move_probability > random.random():
            return True
        else:
            return False

    def birth(self, n):
        r"""
        An animal can mate and give birth if there is more than one animal in a cell

        There is a given probability for an animal giving birth:

        **Calculates probability for birth**

        .. math::
            \begin{equation}
            min(1, \gamma \times \Phi \times (n-1))
            \end{equation}

        If the weight of an animal is less than a given difference, the probability is 0:

        **Difference**

        .. math::
            \begin{equation}
            w < \Xi \times (w_birth + \sigma_birth)
            \end{equation}

        An animal can give max one offspring per year

        At birth the mother lose a given weight

        *If this weight is more than her own weight there is no offspring*

        :param n: amount animals in one cell
        :type n: int

        :return: Weight of newborn animal
        :rtype: float
        """
        birth_prob = 0

        if self.weight < self.parameters['zeta'] * (self.parameters['w_birth'] + self.parameters['sigma_birth']):
            return None

        birth_prob = min(1, self.parameters['gamma'] * self.fitness * (n - 1))
        if random.random() < birth_prob:
            wt = self.calc_birth_weight()
            if wt * self.parameters["xi"] < self.weight:
                self.weight -= wt * self.parameters["xi"]
                self.calc_fitness()
                return type(self)(0, wt)
            else:
                return None
        else:
            return None

    def death(self):
        r"""
        An animal die with certainty if weight = 0

        And with the probability:

        **probability for death**

        .. math::

            \begin{equation}
            \Omega \times (1 - \Phi)
            \end{equation}

        :return: if an animal must be removed from simulation because of death
        :rtype: bool
        """
        if self.weight <= 0:
            return True
        elif random.random() < self.parameters['omega'] * (1 - self.fitness):
            return True
        return False

class Herbivores(Animals):
    """
    Subclass of Animals for the herbivores
    """
    # given parameter for herbivore
    parameters = {'w_birth': 8.0,
                  'sigma_birth': 1.5,
                  'beta': 0.9,
                  'eta': 0.05,
                  'a_half': 40.0,
                  'phi_age': 0.6,
                  'w_half': 10.0,
                  'phi_weight': 0.1,
                  'mu': 0.25,
                  'gamma': 0.2,
                  'zeta': 3.5,
                  'xi': 1.2,
                  'omega': 0.4,
                  'F': 10.0,
                  'DeltaPhiMax': None
                  }

    @property
    def species(self):
        """
        :return: which species
        :rtype: str
        """
        return 'Herbivore'

    def __init__(self, age=None, weight=0):
        """
        **Constructor**

        :param age: Age of the herbivore
        :type age: int

        :param weight: Weight of the herbivore
        :type weight: float
        """
        super().__init__(age, weight)


class Carnivores(Animals):
    """
    Subclass of Animals for the carnivores
    """
    # given parameter for carnivore
    parameters = {'w_birth': 6.0,
                  'sigma_birth': 1.0,
                  'beta': 0.75,
                  'eta': 0.125,
                  'a_half': 40.0,
                  'phi_age': 0.3,
                  'w_half': 4.0,
                  'phi_weight': 0.4,
                  'mu': 0.4,
                  'gamma': 0.8,
                  'zeta': 3.5,
                  'xi': 1.1,
                  'omega': 0.8,
                  'F': 50.0,
                  'DeltaPhiMax': 10.0
                  }

    @property
    def species(self):
        """
        :return: which species
        :rtype: str
        """
        return 'Carnivore'

    def __init__(self, age=None, weight=0):
        """
        **Constructor**

        :param age: Age of the carnivore
        :type age: int

        :param weight: Weight of the carnivore
        :type weight: float
        """
        super().__init__(age, weight)

    def probability_kill(self, fitness_herbivores):
        r"""
        A carnivore will kill a herbivore with a given probability

        **Probability for a carnivore killing a herbivore**

        .. math::

            \begin{equation}
            (\Phi_carnivore - \Phi_herbivore) / \Delta\Phi_Max
            \end{equation}

        :param fitness_herbivores: fitness of herbivore
        :type fitness_herbivores: float

        :return: Calculates the probability of a carnivore killing a herbivore.
        :rtype: float
        """
        if self.fitness <= fitness_herbivores:
            return 0
        elif self.fitness - fitness_herbivores < self.parameters["DeltaPhiMax"]:
            return (self.fitness - fitness_herbivores) / self.parameters["DeltaPhiMax"]
        else:
            return 1

    def killing(self, fitness_herbivores):
        """
        A random carnivore will kill a herbivore with the lowest fitness

        :param fitness_herbivores: fitness of herbivore
        :type fitness_herbivores: float

        :return: Implements a random number to decide if a carnivore will kill a herbivore
        :rtype: bool
        """
        random_number = random.random()
        probability = self.probability_kill(fitness_herbivores)
        if random_number <= probability:
            return True
        else:
            return False
