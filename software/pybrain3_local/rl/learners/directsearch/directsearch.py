# The code for all black-box optimization algorithms is located in  
# the pybrain3_local/optimization directory (to avoid duplicating files). 
# Those algorithms can perfectly be used on (episodic) RL tasks anyway.
#
# See also examples/optimization/optimizers_for_rl.py

__author__ = 'Tom Schaul and Thomas Rueckstiess, tom@idsia.ch, ruecksti@in.tum.de'

from pybrain3_local.rl.learners.learner import Learner, EpisodicLearner


class DirectSearchLearner(Learner):
    """ The class of learners that (in contrast to value-based learners) 
    searches directly in policy space.
    """