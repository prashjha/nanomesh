import logging
import sys

from .mesh import LineMesh, TetraMesh, TriangleMesh
from .mesh2d import Mesher2D, compare_mesh_with_image
from .mesh3d import Mesher3D
from .mesh_container import MeshContainer
from .plane import Plane
from .region_markers import RegionMarker
from .triangulate import simple_triangulate
from .volume import Volume

logging.basicConfig(format='%(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)

__author__ = 'Nicolas Renaud'
__email__ = 'n.renaud@esciencecenter.nl'
__version__ = '0.5.0'

__all__ = [
    '__author__',
    '__email__',
    '__version__',
    'compare_mesh_with_image',
    'LineMesh',
    'Mesher2D',
    'Mesher3D',
    'MeshContainer',
    'Plane',
    'simple_triangulate',
    'TetraMesh',
    'RegionMarker',
    'TriangleMesh',
    'Volume',
]
