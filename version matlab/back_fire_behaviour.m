function [bros, bfi, bfc, back_firetype] =  back_fire_behaviour(ftype, sfc, brss, csi, rso, fmc, bisi, CFL)
  
    bsfi = fire_intensity(sfc, brss) ;
    back_firetype = "surface" ;
    
    if bsfi > csi
        back_firetype = "crown" ;
    end
    
    if back_firetype == "crown"
       bcfb = max(1 - exp(-0.23 * (brss - rso)), 0.0) ; % crown fraction burned
       bcfc = CFL(ftype) * bcfb ;
       bros = final_ros(ftype, fmc, bisi, bcfb, brss) ;
       
       bfc = bcfc + sfc ;
       bfi = fire_intensity(bfc, bros) ;
       return
    else
        bros = brss ;
        bfi = bsfi ;
        bfc = sfc ;
    end
end


 