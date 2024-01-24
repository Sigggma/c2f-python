function sfc = surf_fuel_consump(ft,wdfh,FuelConst2)
    % sfc : surface fuel consumption
    bui = wdfh(1,'BUI').Variables ;   % bui: buildup index
    ffmc = wdfh(1,'FFMC').Variables ; % ffmc: fine fuel moisture code
    
    gfl = FuelConst2("gfl") ;  % gfl : Grass Fuel Load
    pc = FuelConst2("pc") ;    % 
         
    if (ft == "C1")
        if(ffmc > 84) 
            sfc = 0.75 + 0.75 * sqrt(1-exp(-0.23*(ffmc-84) ));
        else  
            sfc = 0.75 - 0.75 * sqrt(1 - exp(0.23 * (ffmc - 84))) ;
        end
        if sfc < 0
            sfc = 0 ;
        end
        return 
    end   
 
    if ( ft == "C2" || ft == "M3" || ft == "M4")
            sfc = 5.0*(1.0-exp(-0.0115*bui)) ;
            return
    elseif (ft == "C3" || ft == "C4")
        sfc = 5.0 * power(1.0-exp(-0.0164*bui) , 2.24) ;
        return
    elseif(ft == "C5" || ft == "C6")
        sfc =  5.0* power(1.0-exp(-0.0149*bui), 2.48) ;
        return
    elseif (ft == "C7")
        ffc = 2.0 * (1.0-exp(-0.104*(ffmc-70.0)));
        if(ffc < 0)
            ffc = 0.0;
        end
        wfc = 1.5 * (1.0-exp(-0.0201*bui));
        sfc = ffc + wfc;
        return
    elseif(ft == "O1a" || ft == "O1b") 
        sfc = gfl ; 
    elseif (ft == "M1" || ft == "M2")
        sfc_c2 = 5.0*(1.0-exp(-0.0115*bui));
        sfc_d1 = 1.5*(1.0-exp(-0.0183*bui));
        sfc = pc/100.0 * sfc_c2 + (100.0-pc)/100.0 * sfc_d1;
        return
    elseif (ft == "S1")
        ffc = 4.0 * (1.0-exp(-0.025*bui));
        wfc = 4.0 * (1.0-exp(-0.034*bui));
        sfc = ffc + wfc;
        return
    elseif(ft == "S2")
      ffc = 10.0*(1.0-exp(-0.013*bui));
      wfc = 6.0*(1.0-exp(-0.060*bui));
      sfc = ffc + wfc;
      return
    elseif (ft == "S3")
      ffc = 12.0 * (1.0-exp(-0.0166*bui));
      wfc = 20.0*(1.0-exp(-0.0210*bui));
      sfc = ffc + wfc;
      return
    elseif(ft == "D1") 
        sfc = 1.5*(1.0 - exp(-0.0183*bui));
        return
    elseif(ft == "D2")
        if bui >= 80
            sfc = 1.5*(1.0-exp(-0.0183*bui)) ;
        else
            sfc = 0 ;
        end
        return
    end
end
    
