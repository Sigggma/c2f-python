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


%% Foliar Moisture Content
x = 1:365;
y = zeros(1,365);
for i = x % i represents of julian day 
    y(i) = foliar_moisture(lat,long,elev,i) ;
end
fig1 = plot(x,y,'-.') ;
xlabel('Julian day','FontSize',14)
ylabel('FMC [%]','FontSize',14)
fig1.Parent.Box = 'off' ;
ylim([0,140])
%% Rate of Spread

ps = 0 ;
saz = 0 ;
x = [0,5,10,20,30,40,50,60] ;
y = zeros(1,length(x));
for i = 1:length(x)
    wdfh(1,"WS").Variables = x(i) ;
    %y(i) = ros_base(ftype, isi, wdfh, a, b, c, FuelConst2)
    y(i) = rate_of_spread(ftype,wdfh,a,b,c,ps,saz,FuelConst2,bui0,q) ;
end

%%
t = tiledlayout(2,2);
t.TileSpacing = 'compact';
t.YLabel.String = 'Rate of Spread [m/min]';
t.YLabel.FontSize = 18;
t.XLabel.String = 'Wind Speed [Km/h]' ;
t.XLabel.FontSize = 18 ;

% C1
ax1 = nexttile ;
plot(x,y,'o')
hold on

p1 = 5.223 ;
p2 = 0.1658 ;
p3 = 0.01366 ;
fHROS = @(x) 1./(p1.*exp(-p2.*x)+p3) ;
fplot(fHROS)
xlim([0,60])
xlabel('FFMC = 90, DMC = 43, DC = 259')
xticks([0:10:60])
grid on
ax1.Box = 'off' ;
ax1.Title.String = 'Fuel Type C1 - FBP System' ;
legend(ax1,'R-square = 0.9992')

% PL01

ax2 = nexttile ;
Fmc = FactorCombustible.valor(19) ;
Fch = function_ch(chD1L1) ;
Fv = FactorViento(2:27,2) ;
HROSdataPL01 = Fmc * Fch * (1 + Fv) ;
plot(ws, HROSdataPL01,'o') ;
hold on

p1 =     0.06332 ;
p2 =      0.1599 ;
p3 =     0.01836 ;

%  R-square: 0.9967
%  Adjusted R-square: 0.9964

fHROS = @(x) 1 ./ (p1.*exp(-p2*x)+p3) ; % [m/min]
fplot(fHROS)
xlim([0,60])
xlabel('FMC = 4%')
xticks([0:10:60])
ax2.Box = 'off' ;
ax2.Title.String = 'Fuel Type PL01 - KITRAL System' ;
legend(ax2,'R-square = 0.9964')
grid on

ax3 = nexttile ;
x1 = [0,1, 5, 10,15, 20,25, 30,35, 40,45, 50,55, 60] ;
y1 = [0.4  0.6	2.5	6.1	10.6	15.8	21.5	27.8	34.6	41.7	49.3	57.3	65.6	74.2];

plot(x1, y1,'o') ;
hold on

p1 = 0.2802 ;
p2 = 0.07786 ;
p3 = 0.01123 ;

% R-square: 0.9944
% Adjusted R-square: 0.9933

fHROS = @(x) 1 ./ (p1.*exp(-p2.*x)+p3) ; % [m/min]
fplot(fHROS)
xlim([0,60])
xlabel('1-h = 3%, 10-h = 4%, 100-h = 5%, LHM = 30%, LWM = 60%')
xticks([0:10:60])
ax3.Box = 'off' ;
ax3.Title.String = 'Fuel Type 10 - Rothermel Models' ;
legend(ax3,'R-square = 0.9933')
grid on

ax4 = nexttile ;
x1 = [0,1, 5, 10,15, 20,25, 30,35, 40,45, 50,55, 60] ;
y1 = [0.6	0.8	3.1	8.5	15.9	24.9	35.5	47.5	60.8	75.3	91.0	107.9	125.8	144.7] ;
plot(x1, y1,'o') ;
hold on

% R-square: 0.9957
% Adjusted R-square: 0.995

p1 = 0.1843 ;
p2 = 0.07911 ;
p3 = 0.005477 ;

fHROS = @(x) 1 ./ (p1.*exp(-p2.*x)+p3) ; % [m/min]
fplot(fHROS)
xlim([0,60])
xlabel('1-h = 3%, 10-h = 4%, 100-h = 5%, LHM = 30%, LWM = 60%')
xticks([0:10:60])
yticks([0:20:150])
ax4.Box = 'off' ;
ax4.Title.String = 'Fuel Type TU4 (164) - Scott & Burgan Models' ;
legend(ax4,'R-square = 0.9957')
grid on

%% Length to Breadth
t = tiledlayout(2,2);
t.TileSpacing = 'compact';
t.YLabel.String = 'Length-to-breath (LB)';
t.YLabel.FontSize = 18;
t.XLabel.String = 'Wind Speed [Km/h]' ;
t.XLabel.FontSize = 18 ;

x1 = [0,1, 5, 10,15, 20,25, 30,35, 40,45, 50,55, 60] ;
y1 = l2bFBP("C1",x1);


ax1 = nexttile ;
plot(x1,y1,'o')

hold on
l1 =  3.053  ;
l2 = 0.02667 ;
%R-square: 0.9999

lbgFBP1 = @(x) 1.0 + (l1*(1-exp(-l2*x))).^2;

fplot(lbgFBP1)
xlim([0,60])
ylim([0,8])

xticks(0:5:60)
yticks(0:1:8)
yticks(0:1:8)
grid on
ax1.Box = 'off' ;
ax1.Title.String = 'LB FBP System' ;


hold on
plot(x1,y2,'o')
l1 = 2.454 ;
l2 = 0.07154 ;
lbgFBP2 = @(x) 1.0 + (l1*(1-exp(-l2*x))).^2;
fplot(lbgFBP2)
legend(ax1,{'Others, R-square = 0.999','','Grass, R-square = 0.969',''},'FontSize',12,'Location',"northwest")

%% Anderson
ax2 = nexttile ;
y3 = l2bAnderson1983("dense-forest-stand",x1) ; % 
plot(x1,y3,'o')

xticks(0:5:60)
xlim([0,60])
grid on

l1 = 1.411 ;
l2 = 0.01745 ;

% R-square: 0.9937
% Adjusted R-square: 0.9932

lbAnderson1 = @(x) 1.0 + (l1*(1-exp(-l2*x))).^2;
hold on
fplot(lbAnderson1)

%------------------
y4 = l2bAnderson1983("open-forest-stand",x1) ; 
plot(x1,y4,'o')
hold on
l1 = 2.587 ;
l2 = 0.01142 ;
% R-square: 0.9951
% Adjusted R-square: 0.9947

lbAnderson2 = @(x) 1.0 + (l1*(1-exp(-l2*x))).^2;
fplot(lbAnderson2)

%---------------------
y5 = l2bAnderson1983("grass-slash",x1) ; 
plot(x1,y5,'o')
hold on
l1 =  5.578 ;
l2 = 0.006023 ;

% R-square: 0.9962
%  Adjusted R-square: 0.9959

lbAnderson3 = @(x) 1.0 + (l1*(1-exp(-l2*x))).^2;
fplot(lbAnderson3)

% --------------------------
y6 = l2bAnderson1983("heavy-slash",x1) ; 
plot(x1,y6,'o')
hold on
l1 = 37.49 ;
l2 =  0.0009885 ;

% R-square: 0.997
% Adjusted R-square: 0.9968

lbAnderson4 = @(x) 1.0 + (l1*(1-exp(-l2*x))).^2;
fplot(lbAnderson4)

%------------------
y7 = l2bAnderson1983("crown-fire",x1) ; 
plot(x1,y7,'o')
hold on
l1 = 3432 ;
l2 = 3.497e-05 ;
%  R-square: 0.9095
%  Adjusted R-square: 0.9019

lbAnderson5 = @(x) 1.0 + (l1*(1-exp(-l2*x))).^2;
fplot(lbAnderson5)

grid on
ax2.Box = 'off' ;
ax2.Title.String = 'Anderson (1983)' ;

legend(ax2,{'dense-forest-stand, R-square = 0.993','',...
            'open-forest-stand, R-square = 0.995','',...
            'grass-slash, R-square = 0.996','',...
            'heavy-slash, R-square = 0.997'},...
            'FontSize',12,'Location',"northwest")


% --------------------------- Alexander 1985 -----------------------------%

ax3 = nexttile ;

y8 = l2bAlexander1985(x1) ;
plot(x1,y8,'o')
hold on

l1 = 3.063 ;
l2 = -0.01165 ;

%  R-square: 0.9977
%  Adjusted R-square: 0.9975
  

lbAlexander = @(x) 1.0 + (l1*(1-exp(-l2*x))).^2;
fplot(lbAlexander)

xticks(0:5:60)
xlim([0,60])
ylim([0,11])
grid on


ax3.Box = 'off' ;
ax3.Title.String = 'Alexander (1985)' ;
legend(ax3,'R-square = 0.9977','FontSize',12,'Location',"northwest")

% ----------------------------

ax4 = nexttile ;
x2 = 0:25;
plot(0:25,LB,'o')
hold on

l1 =     2.233 ;
l2 =    -0.01031 ;

% R-square: 0.9848
%  Adjusted R-square: 0.9838
lbKITRAL = @(x) 1.0 + (l1*(1-exp(-l2*x))).^2;
fplot(lbKITRAL)

ax4.Box = 'off' ;
ax4.Title.String = 'KITRAL System' ;
legend(ax4,'R-square = 0.9848','FontSize',12,'Location',"northwest")
grid on
xlim([0,60])
ylim([0,7])
