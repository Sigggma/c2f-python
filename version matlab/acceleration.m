function accn = acceleration(ftype, cfb)

    open_list = ["O1a","O1b","C1","S1","S2","S3"] ; % open fuel
    
    r = find(ftype == open_list) ;
    if isempty(r)
        % for closed fuels
        accn = 0.115 - 18.8 * cfb^2.5 * exp(-8.0 * cfb) ; % Eq.72
    else
        % for open fuels
        accn = 0.115;
    end
end