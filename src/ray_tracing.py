from numba import njit, prange
import numpy as np


@njit(cache=True, fastmath=True)
def trace_rays_numba(wallmap: np.ndarray, lightmap: np.ndarray,
                     light_x: float, light_y: float,
                     lightmap_scale: int,
                     radius: float,
                     color_r: float, color_g: float, color_b: float):

    H, W = wallmap.shape
    LH, LW = lightmap.shape[0], lightmap.shape[1]

    lightmap[:] = 0.0

    # The number of rays adapts automatically to the radius
    # to avoid gaps.
    nb_rays = int(2.0 * np.pi * radius) + 1
    two_pi = 2.0 * np.pi

    for ray_id in range(nb_rays):
        px = light_x
        py = light_y
        
        prev_lightmap_x = -1
        prev_lightmap_y = -1

        angle = two_pi * (ray_id / nb_rays)
        dx = np.cos(angle)
        dy = np.sin(angle)

        for step in range(int(radius)):
            new_x = px + dx
            new_y = py + dy

            wall_x = int(new_x)
            wall_y = int(new_y)

            if not (0 <= wall_y < H and 0 <= wall_x < W):
                break

            if wallmap[wall_y, wall_x]:
                break

            px, py = new_x, new_y
            lightmap_x = wall_x // lightmap_scale
            lightmap_y = wall_y // lightmap_scale

            if 0 <= lightmap_y < LH and 0 <= lightmap_x < LW:
                if lightmap_x != prev_lightmap_x or lightmap_y != prev_lightmap_y:
                    # linear falloff: 1.0 at the center, 0.0 at the radius
                    falloff = 1.0 - (step / radius)
    
                    lightmap[lightmap_y, lightmap_x, 0] += color_r * falloff * lightmap_scale
                    lightmap[lightmap_y, lightmap_x, 1] += color_g * falloff * lightmap_scale
                    lightmap[lightmap_y, lightmap_x, 2] += color_b * falloff * lightmap_scale
                    
                    prev_lightmap_x = lightmap_x
                    prev_lightmap_y = lightmap_y


@njit(cache=True, fastmath=True, parallel=True)
def pack_lightmap_rgba(lightmap: np.ndarray, rgba_map: np.ndarray):
    H, W = lightmap.shape[0], lightmap.shape[1]
    for y in prange(H):
        for x in range(W):
            v0 = lightmap[y, x, 0]
            v1 = lightmap[y, x, 1]
            v2 = lightmap[y, x, 2]

            rgba_map[y, x, 0] = int(v0) if v0 < 255.0 else 255
            rgba_map[y, x, 1] = int(v1) if v1 < 255.0 else 255
            rgba_map[y, x, 2] = int(v2) if v2 < 255.0 else 255
