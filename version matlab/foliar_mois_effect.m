function rsc = foliar_mois_effect(isi,fmc)
    fme_avg = 0.778 ;
    fme = 1000.0 * (1.5 - 0.00275*fmc)^4.0 / (460.0 + 25.9 * fmc) ;
    rsc = 60.0 * (1.0 - exp(-0.0497 * isi)) * fme / fme_avg ; 
end