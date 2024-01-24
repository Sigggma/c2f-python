function bros = backfire_ros(ftype, bisi, wdfh, a, b, c, FuelConst2, bui0, q)
  
    bros = ros_base(ftype, bisi, wdfh, a, b, c, FuelConst2) ;
    bros = bros * bui_effect(wdfh, bui0(ftype), q(ftype));
end
    
