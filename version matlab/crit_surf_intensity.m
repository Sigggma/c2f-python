function csi = crit_surf_intensity(cbh, fmc)
   % subida copas
   % cbh : crown base hight [m]
   % fmc : foliar moisture content [%]
   csi = 0.001 * cbh^1.5 * (460.0 + 25.9 * fmc)^1.5 ;
end