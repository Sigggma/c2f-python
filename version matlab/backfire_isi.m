function bisi = backfire_isi(wsv, ff)
    % ff: FFMC function from the ISI
    % bisi: ISI used to compute the bros
    % bfw: back fire wind function
    % wsv: wind speed
    bfw = exp(-0.05039 * wsv); % Eq.75
    bisi = 0.208 * ff * bfw ; % Eq.76
end