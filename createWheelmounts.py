import subprocess
from build123d import *
from bd_warehouse.thread import IsoThread


# spacing is the distance between the center of the holes
config = {
    'X spacing': 35,
    'Y spacing': 28,
    'X padding': 1.5,
    'Y padding': 0,
    'margin': 3,
    'plate thickness': 8,
    'hole X offset': 0,
    'plate offset': 0,
    'fillet': 2,
    'flat hole': {
        'X offset': 4.7 + 11.575,
        'Y offset': 1.9,
    },
    'extruded hole': {
        'X offset': 27.6,
    },
    'mount length': 44,
    'mount width': 19,
}

boxWidth = config['X spacing'] + 2 * (config['margin'] + config['X padding'])
boxHeight = config['Y spacing'] + 2 * (config['margin'] + config['Y padding'])

plateOffset = config['plate offset']
mountingPlate = import_step('3D-printing-base-foot-mount-v4.STEP')


# # resize mounting plate
mountIntersection = Pos(7.1, -4, 0) * Box(config['mount length'], 30, config['mount width'] )
mountIntersection = fillet(mountIntersection.edges().filter_by(Axis.Y), radius=config['fillet'])
mountingPlate = mountingPlate.intersect(mountIntersection)


# Reposition the mounting plate
mountingPlate = Rot(X=90) * Pos(-7.1, 8, plateOffset) * mountingPlate.cut(Pos(33, 0, 0) * Box(0.001,30,30))


result = Box(boxWidth, boxHeight, config['plate thickness'])
result = fillet(result.edges().filter_by(Axis.Z), radius=config['fillet'])

# standard screws for the case
cutThread = IsoThread(
    major_diameter = 3.5052,
    pitch = 0.7938,
    length = 7,
    external = False,
    mode = "COMBINE",
    end_finishes = ["square", "square"]
)

locThread = Pos(0, 0, -3.5) * cutThread
threadCyl = Cylinder((3.5052 + 0.7938 / 2) / 2 - 0.05, 7)

hole1pos = Pos(config['extruded hole']['X offset'] - config['mount length'] / 2, 0, 5.8)
hole2pos = Pos(config['flat hole']['X offset'] - config['mount length'] / 2, config['flat hole']['Y offset'], 4.5)
boxcutpos = Pos(config['extruded hole']['X offset'] - config['mount length'] / 2, 0, 9.8)
mountingPlate = mountingPlate.cut(
    hole1pos * threadCyl + hole2pos * threadCyl + boxcutpos * Box(6,6,1)
)
result -= hole1pos * threadCyl + hole2pos * threadCyl
result += hole1pos * locThread + hole2pos * locThread

holeLocations = [
    (config['X spacing'] / 2 + config['hole X offset'], config['Y spacing'] / 2, -(config['plate thickness'] -7) / 2),
    (-config['X spacing'] / 2 + config['hole X offset'], config['Y spacing'] / 2, -(config['plate thickness'] -7) / 2),
    (-config['X spacing'] / 2 + config['hole X offset'], -config['Y spacing'] / 2, -(config['plate thickness'] -7) / 2),
    (config['X spacing'] / 2 + config['hole X offset'], -config['Y spacing'] / 2, -(config['plate thickness'] -7) / 2),
]

for loc in holeLocations:
    result = result - Pos(loc) * threadCyl
    mountingPlate = mountingPlate.cut(Pos(loc) * threadCyl)
    result = result + Pos(loc) * locThread # add the threads


result = result.fuse(mountingPlate)


result.export_step("Output/wheelmount-L.step")
mirror(result, Plane.XZ).export_step("Output/wheelmount-R.step")
result.export_stl("Output/wheelmount-L.stl")
mirror(result, Plane.XZ).export_stl("Output/wheelmount-R.stl")
