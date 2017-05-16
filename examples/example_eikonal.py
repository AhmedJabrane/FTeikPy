# -*- coding: utf-8 -*-

"""
This example benchmarks the performances of a ray tracer with the 2D and 3D
Eikonal solvers on a stratified medium.

Author: Keurfon Luu <keurfon.luu@mines-paristech.fr>
License: MIT
"""

import sys, time
sys.path.append("../")
import numpy as np
from raytracer.raytracer import Ray3D
from fteikpy import Eikonal, lay2vel, lay2tt


if __name__ == "__main__":
    # Parameters
    sources = np.loadtxt("sources.txt")
    receivers = np.loadtxt("stations.txt")
    dz, dx, dy = 5., 5., 5.
    nz, nx, ny = 200, 140, 4
    
    # Make a layered velocity model
    lay = 1500. + 250. * np.arange(10)
    zint = 100. + 100. * np.arange(10)
    vel2d = lay2vel(np.hstack((lay[:,None], zint[:,None])), dz, nz, nx)
    vel3d = np.tile(vel2d[:,:,None], ny)
    
    # Ray tracer
    start_time = time.time()
    ray = Ray3D()
    tcalc_ray = ray.lay2tt(sources, receivers, lay, zint)
    print("Ray tracer: %.3f seconds" % (time.time() - start_time))
    
    # Eikonal 2D
    start_time = time.time()
    eik2d = Eikonal(vel2d, (dz, dx), n_sweep = 2)
    tcalc_eik2d = lay2tt(eik2d, sources, receivers)
    print("\nEikonal 2D: %.3f seconds" % (time.time() - start_time))
    print("Mean residual (2D): ", (tcalc_eik2d - tcalc_ray).mean())
    
    # Eikonal 3D
    start_time = time.time()
    eik3d = Eikonal(vel3d, (dz, dx, dy), n_sweep = 1)
    tt = [ eik3d.solve(sources[i,:]) for i in range(sources.shape[0]) ]
    tcalc_eik3d = np.array([ grid.get(receivers[:,2], receivers[:,0], receivers[:,1])
                                for grid in tt ]).transpose()
    print("\nEikonal 3D: %.3f seconds" % (time.time() - start_time))
    print("Mean residual (3D): ", (tcalc_eik3d - tcalc_ray).mean())