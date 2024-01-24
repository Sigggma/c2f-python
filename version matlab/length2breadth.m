function  lb = length2breadth(ftype, ws)

    if(ftype == "O1a" || ftype == "O1b") % grass fuel
        if ws < 1.0
            lb = 1.0;
        else
            lb = 1.1 + ws^0.464; % Eq.80
        end
    else
        lb = 1.0 + 8.729 * (1.0 - exp(-0.030*ws))^2.155 ;
    end
end