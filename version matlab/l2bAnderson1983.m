function lb = l2bAnderson1983(typefire,ws)
    % Anderson 1983
    if typefire == "dense-forest-stand" % dense forest stand
        lb = 0.936 * exp(0.01240*ws) + 0.461 * exp( -0.00748*ws) - 0.397;
    elseif typefire == "open-forest-stand"
        lb = 0.936 * exp(0.01859*ws) + 0.461 * exp( -0.0112*ws) -0.397;
    elseif typefire == "grass-slash"
        lb = 0.936 * exp(0.02479*ws) + 0.461 * exp( -0.0149*ws) -0.397;
    elseif typefire == "heavy-slash"
        lb = 0.936 * exp(0.03099*ws) + 0.461 * exp( -0.0187*ws) -0.397;
    else % crown-fire forest stand
        lb = 0.936 * exp(0.071278*ws) + 0.461 * exp( -0.043*ws) -0.397;
    end
end