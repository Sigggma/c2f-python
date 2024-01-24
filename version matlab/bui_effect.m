 function be = bui_effect(wdfh, bui0, q)
    % constantes:
    % bui0: depende del combustible
    % q: depende del combustible
    
    bui = wdfh(1,'BUI').Variables ;
    bui_avg = 50.0 ;

    if(bui == 0) 
        bui = 1.0 ;
    end
    be = exp(bui_avg * log(q) * ((1.0/bui)-(1.0/bui0) ) );
end