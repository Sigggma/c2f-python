function [sd,rost] = spread_distance(ros,time,a)
  
    rost = ros * (1.0 - exp(-a*time));
    sd = ros * (time + (exp(-a * time)/a) - 1.0 / a);
end