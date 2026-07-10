"""
Generate a triangular mesh (Gmsh 4.1 .msh format) of a square containing
exactly two triangles that are vertex-adjacent (share exactly one vertex
and no edge). Those two triangles form the physical group/entity "tag_0";
every other triangle forms the physical group/entity "ambient". Neither
tag_0 triangle touches the square's boundary, not even at a single vertex.

Each tag_0 triangle is "right": one vertex has two mutually orthogonal,
unit-length edges to the other two vertices. The whole square is built
from a regular grid of unit cells, each split into 2 right triangles by a
single consistent diagonal, which is trivially conforming across the
whole grid (unlike the 3D cube case, no checkerboarding is needed since
cells only ever share full edges, never diagonals).

The two tag_0 triangles come from two cells that touch only at a single
shared diagonal corner: the triangle built at that shared point from each
cell has its right-angle vertex exactly there, so the pair meets at that
one point only.

"ambient" is written first and owns every node in the mesh (nodes shared
by the tag_0 triangles are still declared under the ambient node entity).
"""

import sys

N = 5  # cells per axis; domain is the square [0, N]^2

# Two cells that touch only at the single diagonal corner CELL1 + (1, 1)
# == CELL2.
CELL1 = (1, 1)
CELL2 = (2, 2)


def cell_triangles(i, j):
    """Split cell (i,j) via the BR-TL diagonal into 2 right triangles."""
    bl, br, tr, tl = (i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)
    t1 = [bl, br, tl]  # right angle at bl
    t2 = [br, tr, tl]  # right angle at tr
    return t1, t2


def node_id(i, j):
    return i * (N + 1) + j


def fix_orientation(tri, points):
    """Reorder (v1,v2,v3) if needed so (v2-v1) x (v3-v1) > 0 (CCW)."""
    p1, p2, p3 = (points[v] for v in tri)
    ux, uy = p2[0] - p1[0], p2[1] - p1[1]
    vx, vy = p3[0] - p1[0], p3[1] - p1[1]
    if ux * vy - uy * vx < 0:
        return [tri[0], tri[2], tri[1]]
    return tri


def build_mesh():
    assert tuple(a + 1 for a in CELL1) == CELL2, "CELL2 must be CELL1's diagonal neighbor"

    points = {}
    for i in range(N + 1):
        for j in range(N + 1):
            points[node_id(i, j)] = (float(i), float(j), 0.0)

    ambient_tris = []
    tag0_tris = []

    for i in range(N):
        for j in range(N):
            t1_local, t2_local = cell_triangles(i, j)

            def to_global(local_tri):
                tri = [node_id(x, y) for x, y in local_tri]
                return fix_orientation(tri, points)

            global_t1 = to_global(t1_local)
            global_t2 = to_global(t2_local)

            if (i, j) == CELL1:
                tag0_tris.append(global_t2)  # right angle at shared corner
                ambient_tris.append(global_t1)
            elif (i, j) == CELL2:
                tag0_tris.append(global_t1)  # right angle at shared corner
                ambient_tris.append(global_t2)
            else:
                ambient_tris.append(global_t1)
                ambient_tris.append(global_t2)

    return points, ambient_tris, tag0_tris


def write_msh(path, points, ambient_tris, tag0_tris):
    node_tags = sorted(points.keys())
    tag_to_index = {tag: idx + 1 for idx, tag in enumerate(node_tags)}
    num_nodes = len(node_tags)

    def remap(tri):
        return [tag_to_index[v] for v in tri]

    ambient_bbox = (0.0, 0.0, 0.0, float(N), float(N), 0.0)
    tag0_coords = [points[v] for t in tag0_tris for v in t]
    xs = [c[0] for c in tag0_coords]
    ys = [c[1] for c in tag0_coords]
    tag0_bbox = (min(xs), min(ys), 0.0, max(xs), max(ys), 0.0)

    num_ambient = len(ambient_tris)
    num_tag0 = len(tag0_tris)
    num_elements = num_ambient + num_tag0

    with open(path, "w") as f:
        f.write("$MeshFormat\n4.1 0 8\n$EndMeshFormat\n")

        f.write("$PhysicalNames\n")
        f.write("2\n")
        f.write('2 1 "ambient"\n')
        f.write('2 2 "tag_0"\n')
        f.write("$EndPhysicalNames\n")

        f.write("$Entities\n")
        f.write("0 0 2 0\n")
        f.write("1 {:g} {:g} {:g} {:g} {:g} {:g} 1 1 0\n".format(*ambient_bbox))
        f.write("2 {:g} {:g} {:g} {:g} {:g} {:g} 1 2 0\n".format(*tag0_bbox))
        f.write("$EndEntities\n")

        f.write("$Nodes\n")
        f.write(f"1 {num_nodes} 1 {num_nodes}\n")
        f.write(f"2 1 0 {num_nodes}\n")
        for idx in range(1, num_nodes + 1):
            f.write(f"{idx}\n")
        for tag in node_tags:
            p = points[tag]
            f.write(f"{p[0]:.16g} {p[1]:.16g} {p[2]:.16g}\n")
        f.write("$EndNodes\n")

        f.write("$Elements\n")
        f.write(f"2 {num_elements} 1 {num_elements}\n")

        elem_tag = 1
        f.write(f"2 1 2 {num_ambient}\n")
        for tri in ambient_tris:
            n = remap(tri)
            f.write(f"{elem_tag} {n[0]} {n[1]} {n[2]}\n")
            elem_tag += 1

        f.write(f"2 2 2 {num_tag0}\n")
        for tri in tag0_tris:
            n = remap(tri)
            f.write(f"{elem_tag} {n[0]} {n[1]} {n[2]}\n")
            elem_tag += 1

        f.write("$EndElements\n")


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "nonmanifold_2d_mesh.msh"
    points, ambient_tris, tag0_tris = build_mesh()
    write_msh(out_path, points, ambient_tris, tag0_tris)
    print(f"Wrote {out_path}: {len(points)} nodes, "
          f"{len(ambient_tris)} ambient triangles, {len(tag0_tris)} tag_0 triangles")


if __name__ == "__main__":
    main()
