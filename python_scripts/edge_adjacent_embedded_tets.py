"""
Generate a tetrahedral mesh (Gmsh 4.1 .msh format) of a cube containing
exactly two tetrahedra that are edge-adjacent (share exactly one edge,
i.e. two vertices). Those two tets form the physical group/entity "tag_0";
every other tet forms the physical group/entity "ambient". Neither tag_0
tet touches the cube's boundary, not even at a single vertex.

Each tag_0 tet is "right": one vertex has three mutually orthogonal,
unit-length edges to the other three vertices. The whole cube is built
from a regular grid of unit sub-cubes, each split into 5 tetrahedra (4
right corner tets + 1 regular central tet) using the standard checkerboard
scheme, which alternates which cube corners are cut off so that adjacent
sub-cubes' shared faces triangulate identically. This gives a fully
conforming mesh with no degenerate or low-quality elements: every tet is
either a unit right corner tet (volume 1/6) or a regular tet (volume 1/3).

"ambient" is written first and owns every node in the mesh (nodes shared
by the tag_0 tets are still declared under the ambient node entity).
"""

import sys

N = 4  # sub-cubes per axis; domain is the cube [0, N]^3
TAG0_CUBE = (1, 1, 1)  # which sub-cube's corner tets become tag_0
                       # (must be strictly interior: 1 <= coord <= N-2)

# Same-parity corner sets for the checkerboard 5-tets-per-cube split.
EVEN_CORNERS = [(0, 0, 0), (1, 1, 0), (1, 0, 1), (0, 1, 1)]
ODD_CORNERS = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)]


def corner_tet(corner):
    """The right tet at `corner`: itself plus its 3 unit-edge neighbors."""
    verts = [corner]
    for bit in range(3):
        n = list(corner)
        n[bit] = 1 - n[bit]
        verts.append(tuple(n))
    return verts


def cube_tets(i, j, k):
    """Return (corner_tets, central_tet) as lists of 4 local-bit tuples."""
    if (i + j + k) % 2 == 0:
        corner_set, central = ODD_CORNERS, EVEN_CORNERS
    else:
        corner_set, central = EVEN_CORNERS, ODD_CORNERS
    corner_tets = [corner_tet(c) for c in corner_set]
    return corner_tets, central


def node_id(i, j, k):
    return i * (N + 1) * (N + 1) + j * (N + 1) + k


def fix_orientation(tet, points):
    """Reorder (v1,v2,v3,v4) if needed so (v4-v1).((v2-v1)x(v3-v1)) > 0."""
    p1, p2, p3, p4 = (points[v] for v in tet)
    ux, uy, uz = (p2[c] - p1[c] for c in range(3))
    vx, vy, vz = (p3[c] - p1[c] for c in range(3))
    cross = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
    signed_vol = sum((p4[c] - p1[c]) * cross[c] for c in range(3))
    if signed_vol < 0:
        return [tet[0], tet[1], tet[3], tet[2]]
    return tet


def build_mesh():
    points = {}
    for i in range(N + 1):
        for j in range(N + 1):
            for k in range(N + 1):
                points[node_id(i, j, k)] = (float(i), float(j), float(k))

    ambient_tets = []
    tag0_tets = []

    for i in range(N):
        for j in range(N):
            for k in range(N):
                corner_tets, central = cube_tets(i, j, k)

                def to_global(local_tet):
                    tet = [
                        node_id(i + dx, j + dy, k + dz)
                        for dx, dy, dz in local_tet
                    ]
                    return fix_orientation(tet, points)

                global_corner_tets = [to_global(t) for t in corner_tets]
                global_central = to_global(central)

                if (i, j, k) == TAG0_CUBE:
                    tag0_tets.extend(global_corner_tets[:2])
                    ambient_tets.extend(global_corner_tets[2:])
                    ambient_tets.append(global_central)
                else:
                    ambient_tets.extend(global_corner_tets)
                    ambient_tets.append(global_central)

    return points, ambient_tets, tag0_tets


def tet_volume(points, tet):
    p0, p1, p2, p3 = [points[v] for v in tet]
    import numpy as np
    p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3))
    return abs(np.dot(p1 - p0, np.cross(p2 - p0, p3 - p0))) / 6.0


def write_msh(path, points, ambient_tets, tag0_tets):
    node_tags = sorted(points.keys())
    tag_to_index = {tag: idx + 1 for idx, tag in enumerate(node_tags)}
    num_nodes = len(node_tags)

    def remap(tet):
        return [tag_to_index[v] for v in tet]

    ambient_bbox = (0.0, 0.0, 0.0, float(N), float(N), float(N))
    tag0_coords = [points[v] for t in tag0_tets for v in t]
    xs = [c[0] for c in tag0_coords]
    ys = [c[1] for c in tag0_coords]
    zs = [c[2] for c in tag0_coords]
    tag0_bbox = (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))

    num_ambient = len(ambient_tets)
    num_tag0 = len(tag0_tets)
    num_elements = num_ambient + num_tag0

    with open(path, "w") as f:
        f.write("$MeshFormat\n4.1 0 8\n$EndMeshFormat\n")

        f.write("$PhysicalNames\n")
        f.write("2\n")
        f.write('3 1 "ambient"\n')
        f.write('3 2 "tag_0"\n')
        f.write("$EndPhysicalNames\n")

        f.write("$Entities\n")
        f.write("0 0 0 2\n")
        f.write("1 {:g} {:g} {:g} {:g} {:g} {:g} 1 1 0\n".format(*ambient_bbox))
        f.write("2 {:g} {:g} {:g} {:g} {:g} {:g} 1 2 0\n".format(*tag0_bbox))
        f.write("$EndEntities\n")

        f.write("$Nodes\n")
        f.write(f"1 {num_nodes} 1 {num_nodes}\n")
        f.write(f"3 1 0 {num_nodes}\n")
        for idx in range(1, num_nodes + 1):
            f.write(f"{idx}\n")
        for tag in node_tags:
            p = points[tag]
            f.write(f"{p[0]:.16g} {p[1]:.16g} {p[2]:.16g}\n")
        f.write("$EndNodes\n")

        f.write("$Elements\n")
        f.write(f"2 {num_elements} 1 {num_elements}\n")

        elem_tag = 1
        f.write(f"3 1 4 {num_ambient}\n")
        for tet in ambient_tets:
            n = remap(tet)
            f.write(f"{elem_tag} {n[0]} {n[1]} {n[2]} {n[3]}\n")
            elem_tag += 1

        f.write(f"3 2 4 {num_tag0}\n")
        for tet in tag0_tets:
            n = remap(tet)
            f.write(f"{elem_tag} {n[0]} {n[1]} {n[2]} {n[3]}\n")
            elem_tag += 1

        f.write("$EndElements\n")


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "edge_adjacent_embedded_tets.msh"
    points, ambient_tets, tag0_tets = build_mesh()
    write_msh(out_path, points, ambient_tets, tag0_tets)
    print(f"Wrote {out_path}: {len(points)} nodes, "
          f"{len(ambient_tets)} ambient tets, {len(tag0_tets)} tag_0 tets")


if __name__ == "__main__":
    main()
