function fi = fire_intensity(fc, ros)
  % fc: predicted fuel consumption [kg/m2]
  % ros: predicted rate of spread [m/m]
  fi = 300.0 * fc * ros; % Eq.69 [kW/m]
  
end