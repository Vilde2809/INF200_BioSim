# This script was highly influenced by Hans Plesser's randvis and plotting projects.
import matplotlib.pyplot as plt
import os
import numpy as np
import subprocess


_FFMPEG_BINARY = 'ffmpeg'
_MAGICK_BINARY = 'magick'

# update this to the directory and file-name beginning
# for the graphics files
_DEFAULT_GRAPHICS_DIR = os.path.join('..', 'data')
_DEFAULT_GRAPHICS_NAME = 'dv'
_DEFAULT_IMG_FORMAT = 'png'
_DEFAULT_MOVIE_FORMAT = 'mp4'  # alternatives: mp4, gif


class Visualization:
    """
    Class for Visualization
    """
    default_cmax = {"Herbivore": 175, "Carnivore": 75}
    default_specifications = {'fitness': {'max': 1, 'delta': 0.05},
                              'age': {'max': 60, 'delta': 2},
                              'weight': {'max': 60, 'delta': 2}}

    def __init__(self, island_map, vis_years=None, ymax_animals=None, cmax_animals=None, hist_specs=None,
                 img_dir=None, img_base=None, img_fmt="png", img_years=None):

        """
        **Constructor**

        """

        self.map = island_map.splitlines()
        self.vis_yeas = vis_years
        self.ymax_animals = ymax_animals if ymax_animals is not None else 18000
        self.cmax_animals = cmax_animals if cmax_animals is not None else self.default_cmax
        self.hist_specs = hist_specs if hist_specs is not None else self.default_specifications
        if img_dir is None:
            img_dir = _DEFAULT_GRAPHICS_DIR
        if not os.path.isdir(img_dir):
            os.mkdir(img_dir)
        if img_base is not None:
            self.img_base = os.path.join(img_dir, img_base)
        else:
            self.img_base = os.path.join(img_dir, _DEFAULT_GRAPHICS_NAME)
        self.img_fmt = img_fmt
        self.img_years = img_years
        self.img_ctr = 1

        self._fig = None
        self._map_ax = None
        self._herb_heat_ax = None
        self._herb_heat_plot = None
        self._carn_heat_ax = None
        self._carn_heat_plot = None
        self._count_ax = None
        self._herb_cnt = None
        self._carn_cnt = None
        self._fitness_ax = None
        self._weight_ax = None
        self._age_ax = None

    def update(self, year, ani_cnt, herb_dist, carn_dist, herb_hist, carn_hist):
        """
        Updates graphics with current data and save to file if necessary.

        :param step: current time step
        :param sys_map: current system status (2d array)
        :param sys_mean: current mean value of system
        """

        # self._update_system_map(sys_map)
        self._update_animal_counts(year, ani_cnt["Herbivore"], ani_cnt["Carnivore"])
        self._update_herbmap(herb_dist)
        self._update_carnmap(carn_dist)
        self.histogram_age_update(herb_hist["age"], carn_hist["age"])
        self.histogram_weight_update(herb_hist["wt"], carn_hist["wt"])
        self.histogram_fitness_update(herb_hist["fit"], carn_hist["fit"])
        self._fig.canvas.flush_events()
        self.year_update(year)
        plt.pause(1e-6)
        self.save_graphics()

    def year_update(self, year):
        self.text_ax.set_text("Simulation Results After\nYear {}".format(year))

    def make_movie(self, movie_fmt=None):
        """
        Creates MPEG4 movie from visualization images saved.

        .. :note:
            Requires ffmpeg for MP4 and magick for GIF

        The movie is stored as img_base + movie_fmt
        """

        if self.img_base is None:
            raise RuntimeError("No filename defined.")

        if movie_fmt is None:
            movie_fmt = _DEFAULT_MOVIE_FORMAT

        if movie_fmt == 'mp4':
            try:
                # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
                # section "Compatibility"
                subprocess.check_call([_FFMPEG_BINARY,
                                       '-i', '{}_%05d.png'.format(self.img_base),
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '3.0',
                                       '-pix_fmt', 'yuv420p',
                                       '{}.{}'.format(self.img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: ffmpeg failed with: {}'.format(err))
        elif movie_fmt == 'gif':
            try:
                subprocess.check_call([_MAGICK_BINARY,
                                       '-delay', '1',
                                       '-loop', '0',
                                       '{}_*.png'.format(self.img_base),
                                       '{}.{}'.format(self.img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: convert failed with: {}'.format(err))
        else:
            raise ValueError('Unknown movie format: ' + movie_fmt)

    def save_graphics(self):
        if self.img_base is not None:
            print(self.img_base)
            plt.savefig("{0}_{1:05d}.{2}".format(self.img_base,self.img_ctr,self.img_fmt),dpi=128)
            self.img_ctr+=1

    def _update_animal_counts(self, year, herbs, carns):
        """
        **Updater for the animal count**
        """
        y_data = self._herb_cnt.get_ydata()
        y_data[year] = herbs
        self._herb_cnt.set_ydata(y_data)

        y_data = self._carn_cnt.get_ydata()
        y_data[year] = carns
        self._carn_cnt.set_ydata(y_data)

    def _update_herbmap(self, herbivore_distribution):
        """
        the heatmap for carnivores
        """
        if self._herb_heat_plot is not None:
            self._herb_heat_plot.set_data(herbivore_distribution)
        else:
            self._herb_heat_plot = self._herb_heat_ax.imshow(herbivore_distribution,
                                                             interpolation='sinc',
                                                             vmin=0, vmax=self.cmax_animals["Herbivore"])
            plt.colorbar(self._herb_heat_plot, ax=self._herb_heat_ax,
                         orientation='vertical')

    def _update_carnmap(self, carnivore_distribution):
        """
        the heatmap for carnivores
        """
        if self._carn_heat_plot is not None:
            self._carn_heat_plot.set_data(carnivore_distribution)
        else:
            self._carn_heat_plot = self._carn_heat_ax.imshow(carnivore_distribution,
                                                             interpolation='sinc',
                                                             vmin=0, vmax=self.cmax_animals["Carnivore"])
            plt.colorbar(self._carn_heat_plot, ax=self._carn_heat_ax,
                         orientation='vertical')

    def setup(self, final_step):
        """
        Prepare graphics.

        Call this before calling :meth:`update()` for the first time after
        the final time step has changed.

        :param final_step: last time step to be visualised (upper limit of x-axis)
        """

        # create new figure window
        if self._fig is None:
            self._fig = plt.figure(figsize=(12, 8))

        # Add left subplot for images created with imshow().
        # We cannot create the actual ImageAxis object before we know
        # the size of the image, so we delay its creation.
        if self._map_ax is None:
            self._map_ax = self._fig.add_subplot(3, 3, 1)
            self.plot_map()

        # Add right subplot for line graph of mean.
        if self._count_ax is None:
            self._count_ax = self._fig.add_subplot(3, 3, 3)
            self._count_ax.set_ylim(0, self.ymax_animals)

        self._count_ax.set_xlim(0, final_step + 1)

        if self._herb_cnt is None:
            count_plot = self._count_ax.plot(np.arange(0, final_step + 1),
                                             np.full(final_step + 1, np.nan))
            self._herb_cnt = count_plot[0]
        else:
            x_data, y_data = self._herb_cnt.get_data()
            x_new = np.arange(x_data[-1] + 1, final_step + 1)
            if len(x_new) > 0:
                y_new = np.full(x_new.shape, np.nan)
                self._herb_cnt.set_data(np.hstack((x_data, x_new)),
                                        np.hstack((y_data, y_new)))

        if self._carn_cnt is None:
            count_plot = self._count_ax.plot(np.arange(0, final_step + 1),
                                             np.full(final_step + 1, np.nan))
            self._carn_cnt = count_plot[0]
        else:
            x_data, y_data = self._carn_cnt.get_data()
            x_new = np.arange(x_data[-1] + 1, final_step + 1)
            if len(x_new) > 0:
                y_new = np.full(x_new.shape, np.nan)
                self._carn_cnt.set_data(np.hstack((x_data, x_new)),
                                        np.hstack((y_data, y_new)))

        text_ax = self._fig.add_axes([0.51, 0.51, 0.1, 0.1])
        text_ax.axis("off")
        self.text_ax = text_ax.text(0., 0., "Simulation Results After\nYear ",
               horizontalalignment='center',
               verticalalignment='center',
               transform=text_ax.transAxes, fontsize = 16)
        if self._herb_heat_ax is None:
            self._herb_heat_ax = self._fig.add_subplot(3, 3, 4)

        if self._carn_heat_ax is None:
            self._carn_heat_ax = self._fig.add_subplot(3, 3, 6)

        if self._fitness_ax is None:
            self._fitness_ax = self._fig.add_subplot(3, 3, 7)

        if self._weight_ax is None:
            self._weight_ax = self._fig.add_subplot(3, 3, 8)

        if self._age_ax is None:
            self._age_ax = self._fig.add_subplot(3, 3, 9)

    def plot_map(self):
        """
        plots map with the given RGB color codes
        """

        #                   R    G    B
        rgb_value = {'W': (0.0, 0.0, 1.0),  # blue
                     'L': (0.0, 0.6, 0.0),  # dark green
                     'H': (0.5, 1.0, 0.5),  # light green
                     'D': (1.0, 1.0, 0.5)}  # light yellow

        map_rgb = [[rgb_value[column] for column in row]
                   for row in self.map]

        self._map_ax.imshow(map_rgb)

        self._map_ax.set_xticks(range(len(map_rgb[0])))
        self._map_ax.set_xticklabels(range(1, 1 + len(map_rgb[0])))
        self._map_ax.set_yticks(range(len(map_rgb)))
        self._map_ax.set_yticklabels(range(1, 1 + len(map_rgb)))

        self._map_lgd = self._fig.add_axes([0.375, 0.7, 0.1, 0.4])  # llx, lly, w, h
        self._map_lgd.axis('off')

        for ix, name in enumerate(('Water', 'Lowland',
                                   'Highland', 'Desert')):
            self._map_lgd.add_patch(plt.Rectangle((0., ix * 0.1), 0.3, 0.1,
                                                  edgecolor='none',
                                                  facecolor=rgb_value[name[0]]))
            self._map_lgd.text(0.35, (ix * 0.1) + 0.04, name, transform=self._map_lgd.transAxes)

    def histogram_age_update(self, herbivores, carnivores):
        """
        update histogram for age

        """
        self._age_ax.clear()
        self._age_ax.set_title("Age distribution")
        max = self.hist_specs["age"]["max"]
        bins = int(self.hist_specs["age"]["max"] // self.hist_specs["age"]["delta"])
        self._age_ax.hist(herbivores, bins=bins, color="blue", histtype="step", label="Herbivore", range=(0, max))
        self._age_ax.hist(carnivores, bins=bins, color="red", histtype="step", label="Carnivore", range=(0, max))
        self._age_ax.legend()

    def histogram_fitness_update(self, herbivores, carnivores):
        """
        updates the histogram for fitness

        """
        self._fitness_ax.clear()
        self._fitness_ax.set_title("Fitness distribution")
        max = int(self.hist_specs["fitness"]["max"])
        bins = int(self.hist_specs["fitness"]["max"] // self.hist_specs["fitness"]["delta"])
        self._fitness_ax.hist(herbivores, bins=bins, color="blue", histtype="step", label="Herbivore", range=(0, max))
        self._fitness_ax.hist(carnivores, bins=bins, color="red", histtype="step", label="Carnivore", range=(0, max))
        self._fitness_ax.legend()

    def histogram_weight_update(self, herbivores, carnivores):
        """
        update histogram for the weight

        :param herbivores: animal herbivore
        :param carnivores: animal carnivore
        """
        self._weight_ax.clear()
        self._weight_ax.set_title("Weight distribution")
        max = int(self.hist_specs["weight"]["max"])
        bins = int(self.hist_specs["weight"]["max"] // self.hist_specs["weight"]["delta"])
        self._weight_ax.hist(herbivores, bins=bins, color="blue", histtype="step", label="Herbivore", range=(0, max))
        self._weight_ax.hist(carnivores, bins=bins, color="red", histtype="step", label="Carnivore", range=(0, max))
        self._weight_ax.legend()


