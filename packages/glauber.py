import numpy as np
from packages.controller import SimulationPlane
from tools.utils.general_utils import write_data
from tools.utils import sim_utils

class Glauber(SimulationPlane):
    """ Class for simulating Glauber dynamics in Icing Model

    dimensions: x and y dimension of the cells

    timesteps: number of timesteps for the simulation

    tempurature: between 1 and 5

    sim_type: simulation mode either 'visual' or 'full'
    """
    def __init__(self, dimensions, timesteps, sim_type, tempurature):
        """
        Glauber Constructor

        Tempurature: The Unitary tempurature of the system
        Mode: The sim_type for either a visual or full simulation
        """
        super().__init__(dimensions, timesteps)
        self.tempurature = tempurature
        self.sim_type = sim_type

    def create_cells(self):
        """Re-implemented from base class
        Creates cells for the simulation
        """
        self.cells = np.random.choice([1, -1], size=(self.dimensions, self.dimensions))

    def create_figure(self):
        """ Reimplemented from base class
        Creates base figure elements that are required for visual sim
        """
        super().create_figure()
        self.axes.set_title("Glauber Simulation For {} Cells".format(self.dimensions ** 2))
        self.im = self.axes.imshow(self.cells, interpolation="nearest", animated=True)
        self.fig.colorbar(self.im)

    def start_sim(self):
        """Re-implemented from base class
        Starts the full simulation or visual simulation
        """
        if self.sim_type.lower() == "visual":
            self.create_cells()
            self.create_figure()
            super().start_sim()
        else:
            self.tempurature = np.arange(1, 3, 0.1)
            self.start_full_sim()

    def start_full_sim(self):
        """ Runs the full simulation procedure """
        self.warning_message()
        self.avg_qauntities = []
        for temp in self.tempurature:
            self.create_cells()
            print ("Current Tempurature: {0:.1f}".format(temp))
            for  i in range(self.timesteps):
                if i % 10 == 0:
                    print("Current Sweep: {} out of {}".format(int(i), int(self.timesteps)))
                for j in range(self.dimensions ** 2):
                    self.glauber_procedure(temp)
                if i >= 99 and i % 10 == 0:
                    self.calculate_averages(temp)
        self.finished_sim()

    def calculate_averages(self, tempurature):
        """ Calculate average energies and magnetisation of the system """
        average_energy = sim_utils.calculate_total_energy(self.cells)
        average_mag = sim_utils.calculate_total_mag(self.cells)
        self.avg_qauntities.append("{},{},{}".format(str(tempurature), str(average_energy), str(average_mag)))

    def anim_func(self, i):
        """ Repimplemented from base class
        Used for visual simulation of glauber dynamics
        """
        for i in range(self.dimensions ** 2):
            self.glauber_procedure(self.tempurature)
        self.im.set_array(self.cells)
        self.check_sim()
        yield self.im

    def glauber_procedure(self, temp):
        """Does the Glauber Procedure for the icing model"""
        random_row = np.random.randint(0, self.dimensions)
        random_col = np.random.randint(0, self.dimensions)
        coordinate = (random_row, random_col)
        energy_change = self.check_nieghbours(coordinate)
        outcome = sim_utils.determine_flip_state(energy_change, temp)
        if outcome == True:
            newState = sim_utils.flip_array_state(self.cells[random_row, random_col])
            self.cells[random_row, random_col] = newState

    def check_nieghbours(self, coordinate):
        """ Re-implemented from base class
        Method for checking the closest neighbours in glauber simulation.
        """
        member, nieghbours = super().check_nieghbours(coordinate)
        energy_change = sim_utils.determine_energy_change(member, nieghbours)
        return energy_change

    def finished_sim(self):
        """ Method for finishing the simulation """
        sim_info = "Glauber Simulation of {} Cells and {} TimeSteps\ntemp,avgEnergy,avgMag".format(self.dimensions ** 2, self.timesteps)
        file_parameters = ["Glauber", self.dimensions, self.timesteps]
        write_data(self.avg_qauntities, file_parameters, sim_info)
