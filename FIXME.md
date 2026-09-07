
SUGGESTED FIXES (no particular order):
1. Exception raising (currently a lot of things can go wrong on run; need to protect with try/except/finally)
2. Game ID naming is not very informative (we could maybe make a function that names games apropriately from the config) -> game logs csv is named after seeds
3. Beta sampling of thompson sampler needs to be seeded
4. config.py has a circular import problem that needs to be fixed
5. Memory function of strategies is messy; hard to understand and not scalable. Need to change into more intuitive and scalable design.
6. What's the point of payout_infer??
