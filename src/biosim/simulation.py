"""
Template for BioSim class.
"""

from biosim.island import Rossumoya
from biosim.island import Lowland, Highland, Desert, Water
from biosim.animals import Herbivores, Carnivores
from biosim.visualization import Visualization
import random
import os


# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2021 Hans Ekkehard Plesser / NMBU

_FFMPEG_BINARY = 'ffmpeg'
_MAGICK_BINARY = 'magick'

# update this to the directory and file-name beginning
# for the graphics files
_DEFAULT_GRAPHICS_DIR = os.path.join('../..', 'data')
_DEFAULT_GRAPHICS_NAME = 'dv'
_DEFAULT_IMG_FORMAT = 'png'
_DEFAULT_MOVIE_FORMAT = 'mp4'


class BioSim:
    """
    Class for the BioSim
    """
    def __init__(self, island_map, ini_pop, seed,
                 vis_years=1, ymax_animals=None, cmax_animals=None, hist_specs=None,
                 img_dir=None, img_base=None, img_fmt='png', img_years=None,
                 log_file=None):
        """
            :param island_map: Multi-line string specifying island geography
            :param ini_pop: List of dictionaries specifying initial population
            :param seed: Integer used as random number seed
            :param ymax_animals: Number specifying y-axis limit for graph showing animal numbers
            :param cmax_animals: Dict specifying color-code limits for animal densities
            :param hist_specs: Specifications for histograms, see below
            :param vis_years: years between visualization updates (if 0, disable graphics)
            :param img_dir: String with path to directory for figures
            :param img_base: String with beginning of file name for figures
            :param img_fmt: String with file type for figures, e.g. 'png'
            :param img_years: years between visualizations saved to files (default: vis_years)
            :param log_file: If given, write animal counts to this file

            If ymax_animals is None, the y-axis limit should be adjusted automatically.
            If cmax_animals is None, sensible, fixed default values should be used.
            cmax_animals is a dict mapping species names to numbers, e.g.,
               {'Herbivore': 50, 'Carnivore': 20}

            hist_specs is a dictionary with one entry per property for which a histogram shall be shown.
            For each property, a dictionary providing the maximum value and the bin width must be
            given, e.g.,
                {'weight': {'max': 80, 'delta': 2}, 'fitness': {'max': 1.0, 'delta': 0.05}}
            Permitted properties are 'weight', 'age', 'fitness'.

            If img_dir is None, no figures are written to file. Filenames are formed as

                f'{os.path.join(img_dir, img_base}_{img_number:05d}.{img_fmt}'

            where img_number are consecutive image numbers starting from 0.

            img_dir and img_base must either be both None or both strings.
        """
        self.island = Rossumoya(island_map)
        self.island.addition_of_population(ini_pop)
        random.seed(seed)
        self.current_year = 0
        self.plotting = Visualization(island_map, vis_years, ymax_animals, cmax_animals, hist_specs,
                 img_dir, img_base, img_fmt, img_years)

    def set_animal_parameters(self, species, params):
        """
        Set parameters for animal species.

        :param species: String, name of animal species
        :param params: Dict with valid parameter specification for species

        :raise ValueError: is not a valid species name
        """
        if species == "Herbivore":
            Herbivores.set_parameters(params)
        elif species == "Carnivore":
            Carnivores.set_parameters(params)
        else:
            raise ValueError(species, "is not a valid species name")

    def set_landscape_parameters(self, landscape, params):
        """
        Set parameters for landscape type.

        :param landscape: String, code letter for landscape
        :param params: Dict with valid parameter specification for landscape

        :raise ValueError: is not a valid landscape
        """
        if landscape == "W":
            Water.set_parameters(params)
        elif landscape == "H":
            Highland.set_parameters(params)
        elif landscape == "L":
            Lowland.set_parameters(params)
        elif landscape == "D":
            Desert.set_parameters(params)
        else:
            raise ValueError(landscape, "is not a valid landscape")

    def simulate(self, num_years):
        """
        Run simulation while visualizing the result.

        :param num_years: number of years to simulate
        """
        self.plotting.setup(self.current_year + num_years)

        for years in range(num_years):
            self.island.simulation_cycle()
            self.current_year += 1
            self.plotting.update(self.current_year, self.num_animals_per_species, self.island.herbivores_matrix(), self.island.carnivores_matrix(), self.island.herb_hist_lists(), self.island.carn_hist_lists())
            print(self.num_animals_per_species)

    def add_population(self, population):
        """
        Add a population to the island

        :param population: List of dictionaries specifying population
        """
        self.island.addition_of_population(population)

    @property
    def year(self):
        """Last year simulated."""
        return self.current_year

    @property
    def num_animals(self):
        """
        Total number of animals on island.
        :return: counting of the animals on the island
        :rtype: int
        """
        return self.island.count_animals()

    @property
    def num_animals_per_species(self):
        """Number of animals per species in island, as dictionary."""
        cnt = dict([("Herbivore", 0), ("Carnivore", 0)])
        for cell in self.island.cells.values():
            cnt["Herbivore"] += len(cell.animal_population["Herbivores"])
            cnt["Carnivore"] += len(cell.animal_population["Carnivores"])
        return cnt

    def make_movie(self, movie_fmt=None):
        """Create MPEG4 movie from visualization images saved."""
        self.plotting.make_movie("mp4")

