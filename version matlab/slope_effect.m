function [wsv,raz] = slope_effect(ft, wdfh, a, b, c, saz, ps, FuelConst2, isi, ff, waz)
    pi = 3.1415 ;
    slopelimit_isi = 0.01 ;
    pc = FuelConst2("pc") ;
    pdf = FuelConst2("pdf") ;
    ps = min(ps, 70.0) ;
    sf = exp(3.533 * (ps / 100.0)^1.2) ;
    sf = min(sf, 10.0) ;
    ws = wdfh(1,"WS").Variables ;
    
    s ;
    if saz >= 360.0
        saz = saz - 360.0 ;
    end
    
    
    if ft == "M1" || ft == "M2"
        isf = ISF_mixedwood(ft, a, b, c, isi, pc, sf) ;
    elseif ft == "M3" || ft == "M4"
        isf = ISF_deadfir(ft, a, b, c, isi, pdf, sf) ;
    else
        rsz = ros_base(ft, isi, wdfh, a, b, c, FuelConst2) ;
        rsf = rsz * sf ;
        if rsf > 0.0
            check = 1.0 - power(rsf / a(ft), 1.0 / c(ft)) ;
        else
            check = 1.0 ;
        end
        if check < slopelimit_isi
            check = slopelimit_isi ;
        end
        isf = -1.0 / b(ft) * log(check) ;
    end
    if isf == 0.0
        isf = isi ;
    end

    wse1 = log(isf / (0.208 * ff)) / 0.05039 ;

    if wse1 <= 40.0
        wse = wse1 ;
    else
        if isf > 0.999 * 2.496 * ff
            isf = 0.999 * 2.496 * ff ;
        end
        wse2 = 28.0 - log(1.0 - isf / (2.496 * ff)) / 0.0818 ;
        wse = wse2 ;
    end

    wrad = waz / 180.0 * pi ;
    wsx = ws * sin(wrad) ;
    wsy = ws * cos(wrad) ;
    srad = saz / 180.0 * pi ;
    wsex = wse * sin(srad) ;
    wsey = wse * cos(srad) ;
    wsvx = wsx + wsex ;
    wsvy = wsy + wsey ;
    wsv = sqrt(wsvx * wsvx + wsvy * wsvy) ;
    raz = acos(wsvy / wsv) ;
    raz = raz / pi * 180.0 ;
    if wsvx < 0
        raz = 360 - raz ;
    end
end
