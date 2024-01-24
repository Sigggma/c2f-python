function isf = ISF_mixedwood(ft, a, b, c, isz, pc, sf)
    slopelimit_isi = 0.01 ;
    rsf_c2 = sf * a("C2") * power((1.0 - exp(-1.0 * b("C2") * isz)), c("C2")) ;

    if rsf_c2 > 0.0
        check = 1.0 - power((rsf_c2 / a("C2")), (1.0 / c("C2")));
    else
        check = 1.0 ;
    end
    if check < slopelimit_isi
        check = slopelimit_isi;
    end
    isf_c2 = (1.0 / (-1.0 * b(ft))) * log(check) ;

    if ft == "M2"
        mult = 0.2 ;
    else
        mult = 1.0 ;
    end
    rsf_d1 = sf * (mult * a(ft)) * power((1.0 - exp(-1.0 * b(ft) * isz)), c(ft)) ;

    if rsf_d1 > 0.0
        check = 1.0 - power((rsf_d1 / (mult * a(ft))), (1.0 / c(ft))) ;
    else
        check = 1.0 ;
    end
    if check < slopelimit_isi
        check = slopelimit_isi ;
    end
    isf_d1 = (1.0 / (-1.0 * b(ft))) * log(check) ;
    isf = pc / 100.0 * isf_c2 + (100 - pc) / 100.0 * isf_d1 ;
   
end