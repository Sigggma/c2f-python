function [ffi, ffc,flank_firetype] = flank_fire_behaviour(ftype, sfc, frss, csi, rso, CFL)
    
    flank_firetype = "surface";
    sfi = fire_intensity(sfc, frss) ;
    if sfi > csi
        flank_firetype = "crown" ;
    end
    if flank_firetype == "crown"  
       
       %ffd = fire_description(fcfb);
       fcfb = max(1 - exp(-0.23 * (frss - rso)), 0.0) ; % crown fraction burned
       fcfc = CFL(ftype) * fcfb ;
        
       ffc = fcfc + sfc;
       ffi = fire_intensity(ffc,frss);
    else
        ffi = sfi ;
        ffc = sfc ;
    end
end