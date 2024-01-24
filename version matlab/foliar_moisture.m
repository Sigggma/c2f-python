function fm = foliar_moisture(lat,long,elev,jd)
  
    jd_min = 0 ;
    
    if(jd_min <=0 ) % dispositivo cuando no hay D0
       if(elev < 0)
         latn = 23.4 * exp(-0.0360*(150-long)) + 46.0; % Eq.1
         jd_min = (0.5 + 151.0 * lat/latn);
       else
         latn = 33.7 * exp(-0.0351*(150-long))+43.0;
         jd_min = (0.5 + 142.1 * lat/latn + (0.0172 * elev));
       end
    end
    nd = round(abs(jd - jd_min)) ;
    if(nd >= 30 && nd < 50) 
        fm = (32.9 + 3.17 * nd - 0.0288*nd^2);
    elseif(nd >= 50) 
        fm = 120 ;
    else
        fm = 85.0+0.0189*nd^2 ;
    end
end