from hypothesis import given, strategies as st
from transforms import rotate_x_by
from vectors import add, scale
import math
import numpy as np



# @given(st.lists(st.integers(), min_size=6, max_size=6))
def test_transformation(fn, coords):
    [vx,vy, vz, ux, uy, uz] = coords
    v = (vx, vy, vz)
    u = (ux, uy, uz)
    v1 = fn(v)
    u1 = fn(u)


    print(v1, u1)
    print(fn(add(v, u)), add(v1, u1))
    assert(fn(add(v, u)) == add(v1, u1))

    print(fn(scale(uy, v)), scale(uy, v1))
    assert(fn(scale(uy, v)) == scale(uy, v1))



if __name__ == '__main__':
    test_transformation(rotate_x_by(math.pi / 2), [0,0,1,0,0,-1])






