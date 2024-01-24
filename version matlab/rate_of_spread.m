function [rss, wsv,raz,isi] = rate_of_spread(ftype, wdfh, a, b, c, ps, saz, FuelConst2, bui0, q)
    ffmc = wdfh(1,"FFMC").Variables ;
    ff = ffmc_effect(ffmc) ;
    ws = wdfh(1,"WS").Variables ;
    %waz = 45 ;
    waz = wdfh(1,"WD").Variables + 180.0 ;
    if waz >= 360.0
        waz = waz - 360.0 ;
    end
    isz = 0.208 * ff ;
    if ps > 0
        % wsv tiene problemas, revisar.
        [wsv,raz] = slope_effect(ftype, wdfh, a, b, c, saz, ps, FuelConst2, isz, ff, waz) ;
    else
        wsv = ws ;
        raz = waz ;
    end
    if wsv < 40.0
        fw = exp(0.05039 * wsv) ;
    else
        fw = 12.0 * (1.0 - exp(-0.0818 * (wsv - 28))) ;
    end
    isi = isz * fw ;

    rsi = ros_base(ftype, isi, wdfh, a, b, c, FuelConst2) ;
    rss = rsi * bui_effect(wdfh, bui0(ftype), q(ftype)) ; % Buildup effect
end