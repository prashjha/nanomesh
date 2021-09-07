import os
import pickle
from pathlib import Path

import numpy as np
import pytest
from matplotlib.testing.decorators import image_comparison

from nanomesh.mesh2d import (Mesher2D, close_corner_contour, generate_2d_mesh,
                             subdivide_contour)

# There is a small disparity between the data generated on Windows / posix
# platforms (mac/linux). Allow some deviation if the platforms do not match.
# windows: nt, linux/mac: posix
GENERATED_ON = 'nt'


def block_image(shape=(10, 10)):
    """Generate test array with 4 block quadrants filled with 1 or 0."""
    i, j = (np.array(shape) / 2).astype(int)
    image = np.zeros(shape)
    image[:i, :j] = 1
    image[-i:, -j:] = 1
    return image


@pytest.fixture
def segmented():
    """Segmented binary numpy array."""
    image_fn = Path(__file__).parent / 'segmented.npy'
    image = np.load(image_fn)
    return image


@pytest.mark.xfail(
    os.name != GENERATED_ON,
    raises=AssertionError,
    reason=('No way of currently ensuring meshes on OSX / Linux / Windows '
            'are exactly the same.'))
def test_generate_2d_mesh(segmented):
    """Test 2D mesh generation and plot."""
    expected_fn = Path(__file__).parent / 'segmented_mesh_2d.pickle'

    np.random.seed(1234)  # set seed for reproducible clustering
    mesh = generate_2d_mesh(segmented, max_contour_dist=4, plot=True)

    if expected_fn.exists():
        with open(expected_fn, 'rb') as f:
            expected_mesh = pickle.load(f)
    else:
        with open(expected_fn, 'wb') as f:
            pickle.dump(mesh, f)

        raise RuntimeError(f'Wrote expected mesh to {expected_fn.absolute()}')

    assert mesh.vertices.shape == expected_mesh.vertices.shape
    assert mesh.faces.shape == expected_mesh.faces.shape
    np.testing.assert_allclose(mesh.vertices, expected_mesh.vertices)
    np.testing.assert_allclose(mesh.faces, expected_mesh.faces)


def test_subdivide_contour():
    """Test contour subdivision."""
    contour = np.array([[0, 0], [0, 6], [2, 6], [2, 0], [0, 0]])

    ret = subdivide_contour(contour, max_dist=2)

    expected = np.array([[0., 0.], [0., 2.], [0., 4.], [0., 6.], [2., 6.],
                         [2., 4.], [2., 2.], [2., 0.], [0., 0.]])

    assert np.all(ret == expected)


@pytest.mark.parametrize('coords,is_corner', (
    ([[0, 3], [5, 5], [0, 7]], False),
    ([[0, 3], [5, 5], [3, 0]], True),
    ([[3, 0], [5, 5], [0, 3]], True),
    ([[9, 17], [5, 15], [17, 19]], True),
    ([[9, 5], [7, 4], [4, 0]], True),
    ([[0, 17], [5, 15], [3, 19]], True),
    ([[5, 5], [5, 7], [6, 6]], False),
))
def test_close_contour(coords, is_corner):
    image_chape = 10, 20
    contour = np.array(coords)

    n_rows = contour.shape[1]

    ret = close_corner_contour(contour, image_chape)

    if is_corner:
        ret.shape[1] == n_rows + 1
    else:
        ret.shape[1] == n_rows


@pytest.mark.xfail(
    os.name != GENERATED_ON,
    raises=AssertionError,
    reason=('No way of currently ensuring contours on OSX / Linux / Windows '
            'are exactly the same.'))
@image_comparison(
    baseline_images=['contour_plot'],
    remove_text=True,
    extensions=['png'],
    savefig_kwarg={'bbox_inches': 'tight'},
)
def test_contour_plot(segmented):
    mesher = Mesher2D(segmented)
    mesher.generate_contours(max_contour_dist=5, level=0.5)
    mesher.plot_contour()