data = load('16Abril2021.mat');
Weather = data.Weather;
writetable(Weather, 'Weather.csv');
