import logging.config
import os

from pypet import Environment
from pypet import pypetconstants
import sys

from ltl.optimizees.functions import tools as function_tools
from ltl.optimizees.functions.benchmarked_functions import BenchmarkedFunctions
from ltl.optimizees.functions.optimizee import FunctionGeneratorOptimizee
from ltl.optimizees.functions import tools as function_tools
from ltl.optimizers.gradientdescent.optimizer import GradientDescentOptimizer
from ltl.optimizers.gradientdescent.optimizer import ClassicGDParameters
from ltl.optimizers.gradientdescent.optimizer import StochasticGDParameters
from ltl.optimizers.gradientdescent.optimizer import AdamParameters
from ltl.optimizers.gradientdescent.optimizer import RMSPropParameters
from ltl.paths import Paths
from ltl.recorder import Recorder

import numpy as np
from ltl.logging_tools import create_shared_logger_data, configure_loggers

from NetworkMDP_Optimizee import DLSMDPOptimizee

logger = logging.getLogger('bin.ltl-fun-gd')


def main():
    name = 'LTL-MDP-GD_6_8_TD1'
    try:
        with open('path.conf') as f:
            root_dir_path = f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(
            "You have not set the root path to store your results."
            " Write the path to a path.conf text file in the bin directory"
            " before running the simulation"
        )
    paths = Paths(name, dict(run_no='test'), root_dir_path=root_dir_path)

    print("All output logs can be found in directory ", paths.logs_path)

    traj_file = os.path.join(paths.output_dir_path, 'data.h5')

    # Create an environment that handles running our simulation
    # This initializes a PyPet environment
    env = Environment(trajectory=name, filename=traj_file, file_title=u'{} data'.format(name),
                      comment=u'{} data'.format(name),
                      add_time=True,
                      # freeze_input=True,
                      # multiproc=True,
                      # use_scoop=True,
                      wrap_mode=pypetconstants.WRAP_MODE_LOCK,
                      automatic_storing=True,
                      log_stdout=False,  # Sends stdout to logs
                      log_folder=os.path.join(paths.output_dir_path, 'logs')
                      )
    create_shared_logger_data(logger_names=['bin', 'optimizers'],
                              log_levels=['INFO', 'INFO'],
                              log_to_consoles=[True, True],
                              sim_name=name,
                              log_directory=paths.logs_path)
    configure_loggers()

    # Get the trajectory from the environment
    traj = env.trajectory

    optimizee = DLSMDPOptimizee(traj)

    ## Outerloop optimizer initialization
    parameters = ClassicGDParameters(learning_rate=0.001, exploration_step_size=0.001,
                                     n_random_steps=50, n_iteration=30,
                                     stop_criterion=np.Inf, seed=1234)
    #parameters = AdamParameters(learning_rate=0.01, exploration_step_size=0.01, n_random_steps=15, first_order_decay=0.8,
    #                             second_order_decay=0.8, n_iteration=83, stop_criterion=np.Inf, seed=99)
    # parameters = StochasticGDParameters(learning_rate=0.01, stochastic_deviation=1, stochastic_decay=0.99,
    #                                     exploration_step_size=0.01, n_random_steps=5, n_iteration=100,
    #                                     stop_criterion=np.Inf)
    #parameters = RMSPropParameters(learning_rate=0.01, exploration_step_size=0.01,
    #                               n_random_steps=5, momentum_decay=0.5,
    #                               n_iteration=100, stop_criterion=np.Inf, seed=99)

    optimizer = GradientDescentOptimizer(traj, optimizee_create_individual=optimizee.create_individual,
                                         optimizee_fitness_weights=(-1.,),
                                         parameters=parameters,
                                         optimizee_bounding_func=optimizee.bounding_func,
                                         base_point_evaluations=10)

    # Add post processing
    env.add_postprocessing(optimizer.post_process)

    # Run the simulation with all parameter combinations
    env.run(optimizee.simulate)

    ## Outerloop optimizer end
    optimizer.end(traj)

    # Finally disable logging and close all log-files
    env.disable_logging()


if __name__ == '__main__':
    main()
