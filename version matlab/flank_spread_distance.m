function [fsd, rost, lbt] = flank_spread_distance(hrost,brost, hdist, bdist, lb, a, time)
  
    lbt = (lb - 1.0) * (1.0 - exp(-a*time)) + 1.0;
    rost = (hrost + brost)/(lbt * 2.0);
    fsd = (hdist + bdist)/(2.0 * lbt) ;
end