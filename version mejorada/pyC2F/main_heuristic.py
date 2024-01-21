# coding: utf-8
# Importations
from tqdm import tqdm

# No Warnings
import warnings
warnings.filterwarnings("ignore")

# Inputs and environment generator
from Cell2Fire.ParseInputs import ParseInputs
from make_env_Cell2Fire import make_env

def main():
    # Parse inputs (args)
    args = ParseInputs()
    
    # Make environment
    env = make_env(args)
    state = env.reset()
    
    # Init heuristic object
    env.init_heuristic(runHeur=True, args=args)        
    InitialAction = env.getAction()
    
    # Run episodes/simulations
    for episode in tqdm(range(1, args.nsims + 1)):
        if args.no_output is False:
            print("-------------------------------- Episode", episode, "--------------------------------")

        # Reset the environment for new episode/simulation 
        state = env.reset()
        #print("Initial State:", state)
        
        # Time steps during horizon (or before if we break it)
        for tstep in range(1, args.max_fire_periods * args.sim_years + 1):
            
            # Heuristic actions: if an action is performed (cells to be harvested) or not (-1)
            if tstep > 1:
                action = env.getAction()
            
            # Step: get state, reward, and done flag (following RL env convention)
            # Same harvesting scheme for all instances at the beginning of planning horizon
            if tstep == 1:
                state, reward, done = env.step(InitialAction)
            
            # Next ones, obtain the new action
            else:
                state, reward, done = env.step(action)

            # Output info
            #print("\tReward:", reward)
            #print("\tDone:", done)
            #print("\tState:", state)

            # Breaking condition (done by not available or end of the period)
            if done == 1:
                break


    # Postprocessing: Stats / Heuristics FPV plots / extra information
    if args.stats:
        # Stats: General and "hourly"
        env.statistics()
    
        # FPV plot 
        env.init_heuristic(args=args)
            
        # FPV plot 
        env.FPV_Plot(GlobalPlot=True)


            
            
            
            
        
        
            
            
        
            
        
        
if __name__ == "__main__":
    main()
    