function cover = get_fueltype_number(ftype)
   
   cftype = ["C1","C2","C3","C4","C5","C6","C7","M1","M2","M3","M4","D1","D2"]; 
   if find(find(ftype == cftype) >= 1)
       cover = "c";
   else 
       cover = "n"; % S1, S2, S3, O1a, O1b, 
   end
   
end