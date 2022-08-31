import argparse
from os import path

SEP = '  '
MARKERS_LINE = 1
FACES_SEP = ' '


def parse_vertice_line(line: str):
    return [float(x) for x in line.split(SEP)]

def triangulate(face):
    t, *f = face


def parse_face_line(face_line):
    t, *f = [int(x) for x in face_line]
    return [t, f]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("f")
    args = parser.parse_args()
    with open(args.f) as f:
        lines = f.readlines()

        markers_line = lines[MARKERS_LINE]
        next_line = MARKERS_LINE + 1

        vertices_count, faces_count, _ = markers_line.split(SEP)
        vertices_count = int(vertices_count)
        faces_count = int(faces_count)

        vertices_lines = lines[next_line:next_line + vertices_count]
        faces_lines = lines[next_line + vertices_count:next_line +
                            vertices_count + faces_count]

        vertices = [parse_vertice_line(l) for l in vertices_lines]
        faces = [parse_face_line(l) for l in faces_lines ]

        faces = [[t, [vertices[i] for i in f]] for t,f in faces]



        print("Vertices: %s ... %s" % (vertices[0], vertices[-1]))

        print("Faces: %s ... %s" % (faces[0], faces[-1]))


if __name__ == '__main__':
    main()
