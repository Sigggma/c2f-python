function fd = fire_description(cfb)
  
    if(cfb < 0.1)
        fd = "S";
    elseif(cfb < 0.9 && cfb >= 0.1)
        fd = "I";
    elseif(cfb >= 0.9)
        fd = "C" ;
    else
        fd = "*" ;
    end
end