function rsi = ros_base(ftype, isi, wdfh, a, b, c, FuelConst2)
    ft = ftype ;
    bui = wdfh(1,"BUI").Variables ;
    if isi == -1
        isi = wdfh(1,"ISI").Variables ;
    end

    pdf = FuelConst2("pdf") ;
    cur = FuelConst2("cur") ;
    pc = FuelConst2("pc") ;

    if ft == "O1a" || ft == "O1b"
        if cur >= 58.8
            mu1 = 0.176 + 0.02 * (cur - 58.8) ;
        else
            mu1 = 0.005 * (exp(0.061 * cur) - 1.0) ;
        end
        if mu1 < 0.001
            mu1 = 0.001 ;
        end
        rsi = mu1 * (a(ft) * (1.0 - exp(-b(ft) * isi))^c(ft)) ;
        return
    elseif ft == "M1" || ft == "M2"
        mu1 = pc / 100.0 ;
        mu2_1 = (100 - pc) / 100.0 ;
        mu2_2 = 2 * (100 - pc) / 100.0 ;
        ros_C1 = a("C2") * (1.0 - exp(-b("C2") * isi))^c("C2") ;
        ros_D1 = a("D1") * (1.0 - exp(-b("D1") * isi))^c("D1") ;
        if ft == "M1"
            rsi = mu1 * ros_C1 + mu2_1 * ros_D1 ;
        else
            rsi = mu1 * ros_C1 + mu2_2 * ros_D1 ;
        end
        return
    elseif ft == "M3" || ft == "M4"
        if ft == "M3"
            a3 = 170 * exp(-35.0 / pdf) ;
            b3 = 0.082 * exp(-36.0 / pdf) ;
            c3 = 1.698 - 0.00303 * pdf ;
            rsi = a3 * (1.0 - exp(-b3 * isi))^c3 ;
        else
            a4 = 140 * exp(-35.5 / pdf) ;
            b4 = 0.0404 ;
            c4 = 3.03 * exp(-0.00714 * pdf) ;
            rsi = a4 * (1.0 - exp(-b4 * isi))^c4 ;
        end
        return
    elseif ft == "D2"
        if bui >= 80
            rsi = a(ft) * (1.0 - exp(-b(ft) * isi))^c(ft) ;
        else
            rsi = 0.0 ;
        end
        return
    else
        % Coniferas
        rsi = a(ft) * (1.0 - exp(-b(ft) * isi))^c(ft) ;
    end
end