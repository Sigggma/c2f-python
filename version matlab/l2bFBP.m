function lb = l2bFBP(ft, ws)
  
    if ft == "O1a" || ft == "O1b"
        if ws < 1.0
            lb = 1.0 ;
        else
            % McArthur et al 1982
            lb = 1.1 * ws.^0.464 ;
        end
    else
        lb = 1.0 + 8.729 * (1.0-exp(-0.030*ws)).^2.155 ;
    end
end