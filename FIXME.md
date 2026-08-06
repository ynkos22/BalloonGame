
SUGGESTED FIXES (no particular order):
1. Vectorize balloons for faster compute
2. Exception raising (currently a lot of things can go wrong on run; need to protect with try/except/finally)
3. Don't commit every turn 


6. Probably shouldn't use SQL as memory
7. Nested SQL queries
8. SEEDED balloons 
9. Explore then exploit ID (a bit weird way to do it maybe should use the ratio)
10. Explore then exploit bug: if popping probabilities are extremely high, it averages round down to 0 so never pumps pnl stays 0
11. If a new game is initiated on an existing table, should empty that first