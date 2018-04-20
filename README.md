harness.py, when run, will perform 100 experiments in which a random graph is created and then brute force and LDFI experiments are run on it.

you will need to install graphviz, pulp, and pycosat.

    git clone https://github.com/palvaro/ldfi-py.git

    # haha woops
    ln -s ldfi-py ldfi_py
    python harness.py


# Stuff that still needs to get done:

 1. implement a smart random fault injector
 2. implement a breadth-first fault injector
 3. explore more principled approaches (like Ashtosh and Asha did) to random generation of graphs.
 4. can we *provide* that LDFI is complete w.r.t. this model?  that is, when LDFI gives up that means there ARE NO BUGS.  naively, we would just do unbounded brute-force search to mechanistically prove completeness, but unfortunately in some cases we would need to wait till after the heat death of the universe.
