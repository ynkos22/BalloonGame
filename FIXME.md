
SUGGESTED FIXES (no particular order):
1. Exception raising (currently a lot of things can go wrong on run; need to protect with try/except/finally)
2. Unit tests from previous version is very unscalable, doesn't run anymore. Probably should use a harness like the profiling part so updating stuff gets easier in the future. But, it's not the most important part right now - not a hurry to fix.


