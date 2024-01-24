# General imporations
import os

# Project importations
import Cell2Fire.Cell2Fire as Cell2Fire
from meta_env import Cell2FireEnv_Tactical, Cell2FireEnv_Operational

'''
Initialize the forest environment (object)
'''
def forest(InFolder,
           OutFolder,
           HCells=set(),
           BCells=set(),
           OutMessages=False,
           SaveMem=False,
           trajectories=False,
           nooutput=False,
           MinutesPerWP=60.0,
           verbose=False,
           Max_Fire_Periods=100000,
           TotalYears=10,
           TotalSims=1,
           FirePeriodLen=1.0,
           Ignitions=True,
           WeatherOpt="rows",
           GenData=False,
           IgnitionRad=0,
           seed=0,
           ROS_Threshold=1e-3,
           HFactor=1.0,
           FFactor=1.0,
           BFactor=1.0,
           EFactor=1.0,
           PromTuned=True,
           ROSThreshold=1e-3,
           HFIThreshold=1e-3,
           ROSCV=0.0,
           Stats=False,
           obsSpace=1,
           plotStep=-1,
           plotFreq=60,
           FinalPlot=False,
           gridsFreq=-1,
           gridsStep=60,
           combine=False,
           stats=False,
           heuristic=0,
           msgHeur="",
           GASelection=False):
    
    ForestOB = Cell2Fire.Cell2FireObj(InFolder,                           # Instance folder
                                      OutFolder,                          # Output folder
                                      HCells=set(),                       # Initially harvested cells (if wanted)
                                      BCells=set(),                       # Initially burned cells (if wanted)
                                      OutMessages=OutMessages,            # If fire messages are printed into a txt file
                                      SaveMem=SaveMem,                    # If SaveMem mode is activated (not useful right now)
                                      trajectories=trajectories,          # If we want to save the fire trajectories 
                                      nooutput=nooutput,                  # No info is printed during the sim (False if debugging)
                                      MinutesPerWP=MinutesPerWP,          # Minutes per weather info (default = 60 min = 1 hr)
                                      verbose=verbose,                    # verbosity level 
                                      Max_Fire_Periods=Max_Fire_Periods,  # Maximum duration of the fire dynamic 
                                      TotalYears=TotalYears,              # Number of years to simulate (Horizon)
                                      TotalSims=TotalSims,                # Total number of simulations 
                                      FirePeriodLen=FirePeriodLen,        # Resolution 
                                      Ignitions=Ignitions,                # True if ignition points (or centers) are provided
                                      WeatherOpt=WeatherOpt,              # Weather option
                                      combine=combine,                    # True if plots are combined with background
                                      GenData=GenData,                    # True if we need to generate data (not useful now)
                                      IgnitionRad=IgnitionRad,            # Number of adjacent layers with ignition probability
                                      seed=seed,                          # Random seed used for replications
                                      ROS_Threshold=1e-3,                 # ROS threshold for ignition (keep it as is)
                                      HFactor=HFactor,                    # ROS Factors (keep them as is)
                                      FFactor=FFactor,                    # ROS Factors (keep them as is)
                                      BFactor=BFactor,                    # ROS Factors (keep them as is)
                                      EFactor=EFactor,                    # ROS Factors (keep them as is)
                                      PromTuned=PromTuned,                # ROS Factors (keep them as is)
                                      ROSThreshold=ROSThreshold,          # ROS Factors (keep them as is)
                                      HFIThreshold=HFIThreshold,          # ROS Factors (keep them as is) 
                                      ROSCV=ROSCV,                        # ROS CV: stochasticity of the Rate of Spread  
                                      observationSpace=obsSpace,          # Environment version (observation)
                                      plotStep=plotStep,                  # Plot every plotStep 
                                      plotFreq=plotFreq,                  # Plot every plotFreq episodes
                                      FinalPlot=FinalPlot,                # Generate a final plot
                                      gridsStep=gridsStep,                # Generate grids every gridsStep
                                      gridsFreq=gridsFreq,                # Generate grids every gridsFreq episodes
                                      stats=stats,                        # Statistics flag
                                      heuristic=heuristic,                # Heuristic ID
                                      msgHeur=msgHeur,
                                      GASelection=GASelection)                
    
    # Return object
    return ForestOB

'''
Create the environment
'''
def make_env(args):
    # Object
    forest_env = forest(InFolder=args.input_folder,
                        OutFolder=args.output_folder, 
                        HCells=args.HCells,
                        BCells=set(),
                        OutMessages=args.input_messages,
                        SaveMem=args.input_save,
                        trajectories=args.input_trajectories,
                        nooutput=args.no_output,
                        MinutesPerWP=args.weather_period_len,
                        verbose=args.verbose,
                        Max_Fire_Periods=args.max_fire_periods,
                        TotalYears=args.sim_years,
                        TotalSims=args.nsims,
                        FirePeriodLen=args.input_PeriodLen,
                        Ignitions=args.act_ignitions,
                        WeatherOpt=args.input_weather, 
                        GenData=args.input_gendata,
                        IgnitionRad=args.IgRadius,
                        seed=args.seed, 
                        ROS_Threshold=args.ROS_Threshold,
                        HFactor=args.HFactor,
                        FFactor=args.FFactor,
                        BFactor=args.BFactor,
                        EFactor=args.EFactor,
                        PromTuned=args.PromTuning,
                        ROSThreshold=args.ROS_Threshold,
                        HFIThreshold=args.HFI_Threshold,
                        ROSCV=args.ROS_CV,
                        Stats=args.stats,
                        obsSpace=args.obsSpace,
                        plotStep=args.plotStep,
                        plotFreq=args.plotFreq,
                        FinalPlot=args.fplot,
                        gridsFreq=args.gridsFreq,
                        gridsStep=args.gridsStep,
                        combine=args.input_combine,
                        stats=args.stats,
                        heuristic=args.heuristic,
                        msgHeur=args.msgHeur,
                        GASelection=args.GASelection)
    
    # Sanity check
    if args.version not in ["tactical", "operational"]:
        raise RuntimeError(args.version + "is not supported, use tactical or operational")
    
    # Initialize the meta env
    if args.version == "tactical":
        env = Cell2FireEnv_Tactical(forest_env)
    elif args.version == "operational":
        env = Cell2FireEnv_Operational(forest_env)
        
    # Return environment
    return env
