# -*- coding: utf-8 -*-

import textwrap
import matplotlib.pyplot as plt

from biosim.simulation import BioSim

"""
Compatibility check for BioSim simulations.

This script shall function with biosim packages written for
the INF200 project January 2022.
"""

__author__ = "Hans Ekkehard Plesser, NMBU"
__email__ = "hans.ekkehard.plesser@nmbu.no"


if __name__ == '__main__':

    geogr = """\
               WWWWWWWWWWWWWWWWWWWWW
               WWWWWWWWHWWWWLLLLLLLW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHHHHHWWLLLLLLWWW
               WHHHHHLLLLLLLLLLLLWWW
               WHHHHHLLLDDLLLHLLLWWW
               WHHLLLLLDDDLLLHHHHWWW
               WWHHHHLLLDDLLLHWWWWWW
               WHHHLLLLLDDLLLLLLLLWW
               WHHHHLLLLDDLLLLWWWLWW
               WWHHHHLLLLLLLLWWWLLLW
               WWWHHHHLLLLLLLDDDDLWW
               WWWWWWWWWWWWWWWWWWWWW"""
    geogr = textwrap.dedent(geogr)

    ini_herbs = [{'loc': (10, 10),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(150)]}]
    ini_carns = [{'loc': (9, 6),
                  'pop': [{'species': 'Carnivore',
                           'age': 2,
                           'weight': 45}
                          for _ in range(300)]}]
    new_carns = [{'loc': (4, 13),
                  'pop': [{'species': 'Carnivore',
                           'age': 5,
                           'weight': 30}
                          for _ in range(10)]}]

    sim = BioSim(island_map=geogr, ini_pop=ini_herbs+ini_carns,
                 seed=123456,
                 hist_specs={'fitness': {'max': 1.0, 'delta': 0.05},
                             'age': {'max': 60.0, 'delta': 2},
                             'weight': {'max': 60, 'delta': 2}},
                 vis_years=1)

    sim.set_animal_parameters('Herbivore', {'zeta': 3.2, 'xi': 1.8})
    sim.set_animal_parameters('Carnivore', {'a_half': 60, 'phi_age': 0.5,
                                            'omega': 0.3, 'F': 65,
                                            'DeltaPhiMax': 9.,
                                            "mu":0.9})
    sim.set_landscape_parameters('L', {'f_max': 1200})

    sim.simulate(num_years=100)
    sim.add_population(population=new_carns)
    sim.simulate(num_years=100)
    sim.make_movie()
