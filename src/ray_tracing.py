from numba import njit
import numpy as np


@njit(cache=True, fastmath=True)
def trace_rays_numba(wallmap: np.ndarray, lightmap: np.ndarray,
                     light_x: float, light_y: float,
                     lightmap_scale: int,
                     nb_rays: int, energy_decay: float,
                     bounce_decay: float, min_energy: float):
    H, W = wallmap.shape
    LH, LW = lightmap.shape[0], lightmap.shape[1]
    lightmap[:] = 0.0
    two_pi = 2.0 * np.pi

    for ray_id in range(nb_rays):
        px = light_x
        py = light_y
        # Uses 3 floats for RGB energy.
        e0, e1, e2 = 255.0, 255.0, 255.0

        angle = two_pi * (ray_id / nb_rays)
        dx = np.cos(angle)
        dy = np.sin(angle)

        while (e0 > min_energy or e1 > min_energy or e2 > min_energy):
            new_x = px + dx
            new_y = py + dy

            wall_x = int(new_x)
            wall_y = int(new_y)

            if not (0 <= wall_y < H and 0 <= wall_x < W):
                break

            if wallmap[wall_y, wall_x]:
                vertical_hit = wallmap[int(py), wall_x]
                horizontal_hit = wallmap[wall_y, int(px)]
                if vertical_hit and not horizontal_hit:
                    dx *= -1.0
                elif horizontal_hit and not vertical_hit:
                    dy *= -1.0
                else:
                    dx *= -1.0
                    dy *= -1.0
                e0 *= bounce_decay
                e1 *= bounce_decay
                e2 *= bounce_decay
                continue

            px, py = new_x, new_y
            lightmap_x = wall_x // lightmap_scale
            lightmap_y = wall_y // lightmap_scale

            if 0 <= lightmap_y < LH and 0 <= lightmap_x < LW:
                lightmap[lightmap_y, lightmap_x, 0] += e0
                lightmap[lightmap_y, lightmap_x, 1] += e1
                lightmap[lightmap_y, lightmap_x, 2] += e2

            e0 *= energy_decay
            e1 *= energy_decay
            e2 *= energy_decay


@njit(cache=True, fastmath=True)
def pack_lightmap_rgba(lightmap: np.ndarray, rgba_map: np.ndarray):
    H, W = lightmap.shape[0], lightmap.shape[1]
    for y in range(H):
        for x in range(W):
            v0 = lightmap[y, x, 0]
            v1 = lightmap[y, x, 1]
            v2 = lightmap[y, x, 2]

            if v0 > 255.0:
                v0 = 255.0
            if v1 > 255.0:
                v1 = 255.0
            if v2 > 255.0:
                v2 = 255.0

            rgba_map[y, x, 0] = int(v0)
            rgba_map[y, x, 1] = int(v1)
            rgba_map[y, x, 2] = int(v2)
