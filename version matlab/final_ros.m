function ros = final_ros(ftype, fmc, isi, cfb, rss)
    % rsc : crow fire spread rate [m/min] 
    if(ftype == "C6")
        rsc = foliar_mois_effect(isi, fmc) ;
        ros = rss + cfb * (rsc - rss) ;
    else 
        ros = rss ;
    end
 end