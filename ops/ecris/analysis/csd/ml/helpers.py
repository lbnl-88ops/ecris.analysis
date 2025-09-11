from itertools import permutations

def sorted_permutations(to_permute, permutation_length: int = 7):
    return [list(p) for p in permutations(to_permute, r=permutation_length) 
                                          if list(p) == sorted(p)] 
