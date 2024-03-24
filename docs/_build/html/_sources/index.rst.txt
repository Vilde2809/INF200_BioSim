.. BioSim documentation master file, created by
   sphinx-quickstart on Sun Jan 16 12:44:30 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to BioSim's documentation!
==================================
Welcome to the biological simulation of Rossumoya! This project contains :

 * herbivores and carnivores interacting within a cell
 * both species migrating to neighboring cells
 * a map of the island
 * a heat map of where the species is located
 * histograms for the animals: fitness, age and weight

.. image:: simulation_photo.png

About the task
==============
BioSim is a simulation of the island Rossumoya. It is a small island in the middle of the ocean.
The ecosystem on Rossumoya is characterized by several different landscapes types, such as:

 * Lowland: provides large amounts of fodder even under intense grazing
 * Highland: provides a limited amount of fodder
 * Desert: does not provide fodder for herbivores
 * Water: is impassable for both species

The fauna includes only two species:
 * Herbivores: depend on a good supply of fodder to survive and reproduce
 * Carnivores: depend on the availability of prey. Carnivores are more mobile than herbivores

The Island contains an annual cycle which gives the possibility to take a look into the future.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   BioSim


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
