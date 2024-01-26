%% Constantes

% 18 Fuel Types 
FBPfuelTypes = {'C1','C2','C3','C4','C5','C6', 'C7', 'M1','M2','M3',...
            'M4','D1','D2', 'S1','S2','S3','O1a','O1b'};
        
% Crown fuel load [Kg/m2]
CFLvalues = [0.75, 0.8, 1.15, 1.2, 1.2, 1.8, 0.5, 0.8,...
        0.8, 0.8, 0.8, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] ;
    
% Canopy base Height [m]
CBHvalues = [2.0, 3.0, 8.0, 4.0, 18.0, 7.0, 10.0, 6.0, 6.0, 6.0,...
            6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]; 
        
% Parameter for Basic rate of spread (ISI-equation)         
a_values = [90, 110, 110, 110, 30, 30, 45, 110, 110,...
    120, 100, 30, 6, 75, 40, 55, 190, 250];

b_values = [0.0649, 0.0282, 0.0444, 0.0293, 0.0697, 0.08, 0.0305, 0.0282,...
    0.0282, 0.0572, 0.0404, 0.0232, 0.0232, 0.0297, 0.0438, 0.0829, 0.031, 0.031];

c_values = [4.5, 1.5, 3.0, 1.5, 4.0, 3.0, 2.0, 1.5, 1.5, 1.4, 1.48,...
    1.6, 1.6, 1.3, 1.7, 3.2, 1.4, 1.7];        
% Parameters for Buildup Effect (BE)
qvalues = [0.9, 0.7, 0.75, 0.8, 0.8, 0.8, 0.85, 0.8, 0.8, 0.8, 0.8,...
       0.75, 0.9, 0.75, 0.75, 0.75, 1.0, 1.0] ;

bui0values = [72, 64, 62, 66, 56, 62, 106, 50, 50, 50, 50,...
                32, 32, 38, 63, 31, 1, 1] ;

% Building dictionaries for parameters 
CFL = containers.Map(FBPfuelTypes,CFLvalues) ;
CBH = containers.Map(FBPfuelTypes,CBHvalues) ;
q = containers.Map(FBPfuelTypes,qvalues) ;
bui0 = containers.Map(FBPfuelTypes,bui0values) ;
a = containers.Map(FBPfuelTypes,a_values) ;
b = containers.Map(FBPfuelTypes,b_values) ;
c = containers.Map(FBPfuelTypes,c_values) ;

FuelConst2 = containers.Map;
FuelConst2("pc") = 50 ; % Percent Conifer for M1/M2 [percent]
FuelConst2("pdf") = 35 ; % Percent Dead Fir for M3/M4 [percent]
FuelConst2("gfl") = 0.35 ; % Grass Fuel Load [kg/m^2]
FuelConst2("cur") = 60 ;  % Percent Cured for O1a/O1b [percent]
%% Inputs
% Weather
%{
    Scenario: Name
    datetime: YYYY-MM-DD HH:MM
    APCP  : Precipitation [?]
    TMP   : Temperature [ºC]
    RH    : Ralative humidity [%]
    WS    : Wind Speed [Km/h]
    WD    : Wind direction [º]
    FFMC  : Fine Fuel Moisture Code
    DMC   : Duff Moisture Code
    DC    : Drought Code
    ISI   : Initial Spread Index
    BUI   : Buildup Index
    FWI   : Fire Weather Index
%}

i = 1 ; % row i of Weather file
wdfh = Weather(i,:) ; % table format
ftype = "C1" ; % Example
%% Run Test
% Calculation and loading of parameters
jd = juliandate(wdfh(1,'datetime').Variables) - juliandate(datetime("01-Jan-2001"));
lat = 51.621244 ; % Latitude [º]
long = - 115.608378  ; % Longitude [º]
elev = 2138.0 ; % Geographic elevation [m]
ps = 0 ; % Percentage of slope [%]
saz = 0 ; % slope azimuth (uphill direction) [º]
% waz: wind azimuth (direction) [º]
% wsv: net effective wind speed [Km/h]
% raz: net effective wind direction [º]

%%

% Surface fuel consumption
sfc = surf_fuel_consump(ftype, wdfh, FuelConst2) ; % en [Kg/m2]

% Head Rate of spread (HROS = ROS) (includes slope an buildup effect
[ros,wsv,raz,isi] = rate_of_spread(ftype, wdfh, a, b, c,...
                                ps, saz, FuelConst2, bui0, q) ; % [m/min]

% Surface fire intensity                          
sfi = fire_intensity(sfc, ros) ; % en [kW/m]

% Foliar moisture content
fmc = foliar_moisture(lat, long, elev, jd) ; % en [%]

% Critical surface intensity
csi = crit_surf_intensity(CBH(ftype), fmc) ;

if (ftype >= "C1" && ftype <= "C7") || (ftype >= "M1" && ftype <= "M4") % CBH > 0
    % fire type = crown
    if sfi > csi
        rso = max(csi / (300 * sfc), 0.0)  ; % critical ros
        % crown fraction burned
        cfb = max(1 - exp(-0.23 * (ros - rso)), 0.0) ; 
        % crown fuel consumption
        cfc = CFL(ftype) * cfb ; % en [kg/m2] 
        if ftype == "M1" || ftype == "M2"
            cfc = FuelConst2("pc") / 100.0 * cfc ; % update
        elseif ftype == "M3" || ftype == "M4"
            cfc = FuelConst2("pdf") / 100.0 * cfc ; % update
        end
        %isi = wdfh(1,"ISI").Variables ;
        % ++ crown fire rate of spread
        tfc = sfc + cfc ;
        ros = final_ros(ftype, fmc, isi, cfb, ros) ; 
        % Total fire intensity 
        fi = fire_intensity(tfc,ros) ; 
        firetype = "crown" ;
    end    
        
else % CBH == 0.0
    cfb = 0 ;
    cfc = 0 ;
    tfc = sfc ;
    fi = sfi ;
end

% Fine Fuel Moisture Content
ffmc = wdfh(1,"FFMC").Variables ;

% FFMC effect
ff = ffmc_effect(ffmc) ;

% Length to breadth
lb = length2breadth(ftype, wsv) ;

% Back ISI
bisi = backfire_isi(wsv, ff) ;

% Back rate of spread 
brss = backfire_ros(ftype, bisi, wdfh, a, b, c, FuelConst2, bui0, q) ;

if (ftype >= "C1" && ftype <= "C7") || (ftype >= "M1" && ftype <= "M4") % CBH > 0
    % with crown effect
    [bros, bfi, bfc, back_firetype] =  back_fire_behaviour(ftype, sfc, brss, csi, rso, fmc, bisi, CFL) ;
end

% Flank Rate of Spread
fros = flankfire_ros(ros, bros, lb) ;

% Flank Fire Behavior
[ffi, ffc,flank_firetype] = flank_fire_behaviour(ftype, sfc, fros, csi, rso, CFL) ;
%%
% Elapse time
elapsetime = 60 ; % [min]

% 
accn = acceleration(ftype, cfb) ;

% 
[hdist, hrost] = spread_distance(ros,elapsetime,accn) ;

%
[bdist, brost] = spread_distance(bros,elapsetime,accn) ;

%
[fdist, rost, lbt] = flank_spread_distance(hrost,brost, hdist, bdist, lb, accn, elapsetime) ;

% Area of the Ellipse 
areaelipse = area(hdist + bdist, fdist) ;

% Perimeter of the Ellipse
perelipse = perimeter(hdist, bdist, lb) ;
%% Primary Outputs
fprintf('Primary Outputs: \n')
fprintf('HROS_t = %.3f [m/min] \t\t', hrost)
fprintf('SFC = %.3f [Kg/m2] \n', sfc)

fprintf('HROS_eq = %.3f [m/min] \t', ros)
fprintf('CFC = %.3f [Kg/m2] \n', cfc)

fprintf('HFI = %.3f [kW/m] \t\t', fi)
fprintf('TFC = %.3f [Kg/m2] \n', tfc)

fprintf('CFB = %.3f [Percentage] \t', cfb * 100)
fprintf('Fire description:  %s-fire \n', firetype)
fprintf('\n\n')
%% Secondary Outputs
fprintf('Secondary Outputs: \n')

fprintf('RSO = %.3f [m/min] \t', rso)
fprintf('CSI = %.3f [kW/m] \t', csi)
fprintf('DH = %.3f [m] \t', hdist)
fprintf('LB = %.3f [m] \n', lb)

fprintf('FROS = %.3f [m/min] \t', fros)
fprintf('FFI = %.3f [kW/m] \t', ffi)
fprintf('DF = %.3f [m] \t', fdist)
fprintf('Area = %.3f [ha] \n', areaelipse)

fprintf('BROS = %.3f [m/min] \t', bros)
fprintf('BFI = %.3f [kW/m] \t', bfi)
fprintf('DB = %.3f [m] \t\t', bdist)
fprintf('Perimeter = %.3f [m] \n', perelipse)

