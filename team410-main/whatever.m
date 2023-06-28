data = zeros(1517, 4);
t = 0;
b = 1;
for i = 1:1517
    j = 1;
    k = 0;
    while (k == 0)
        if (Mora(i) == thedata(j, 1))
            data(i, 1) = Mora(i);
            data(i, 2) = thedata(j,2);
            data(i, 3) = thedata(j,4);
            data(i, 4) = thedata(j,3);
            k = 1;
            smalldata(b, :) = data(i, :);
            thelist(b) = i;
            b = b + 1;
        end
        if (j == 3144)
            data(i,1) = Mora(i);
            k = 1;
            t = t + 1;
        end
        j = j + 1;
    end
end
t