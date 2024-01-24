function isf = ISF_deadfir(ft, a, b, c, isz, pdf, sf)
    slopelimit_isi = 0.01;
    rsf_max = sf * a(ft) * power((1.0 - exp(-1.0 * b(ft) * isz)), c(ft)) ;
    if rsf_max > 0.0
        check = 1.0 - power((rsf_max / a(ft)), (1.0 / c(ft))) ;
    else
        check = 1.0 ;
    end
    if check < slopelimit_isi
        check = slopelimit_isi ;
    end
    isf_max = (1.0 / (-1.0 * b(ft))) * log(check) ;

    if ft == "M4"
        mult = 0.2 ;
    else
        mult = 1.0 ;
    end

    rsf_d1 = sf * (mult * a("D1")) * power((1.0 - exp(-1.0 * b(ft) * isz)), c(ft)) ;

    if rsf_d1 > 0.0
        check = 1.0 - power((rsf_d1 / (mult * a(ft))), (1.0 / c(ft))) ;
    else
        check = 1.0 ;
    end
    if check < slopelimit_isi
        check = slopelimit_isi ;
    end
    isf_d1 = (1.0 / (-1.0 * b(ft))) * log(check) ;

    isf = pdf / 100.0 * isf_max + (100.0 - pdf) / 100.0 * isf_d1 ;
end
    