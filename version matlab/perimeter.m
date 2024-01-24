function p = perimeter(hdist, bdist, lb)
  
    pi = 3.1416 ;
    aux = pi * (1.0 + 1.0/lb) * (1.0 + power(((lb-1.0)/(2.0*(lb+1.0))),2.0)) ;
    p = (hdist + bdist)/ 2 * aux ;
end


  