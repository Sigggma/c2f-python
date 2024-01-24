function ff = ffmc_effect(ffmc)
 
   mc = 147.2 * (101.0 - ffmc)/(59.5+ffmc); % Eq.46
   ff = 91.9 * exp(-0.1386 * mc) * (1 + mc^5.31/4.93e7); % Eq.45
end
