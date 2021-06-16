import time
import warnings

import matplotlib.pyplot as plt
import numpy as np
from ipywidgets import IntSlider, RadioButtons, interact

try:
    import pygalmesh
except ImportError:
    pygalmesh = None


class requires:
    """Decorate functions to mark them as unavailable based if `condition` does
    not evaluate to `True`."""
    def __init__(self, *, condition, message='requires optional dependencies'):
        self.condition = condition
        self.message = message

    def __call__(self, func):
        if not self.condition:

            def dummy(*args, **kwargs):
                warnings.warn(f'`{func.__qualname__}` {self.message}.')

            return dummy
        else:
            return func


class SliceViewer:
    """Simple slice viewer for volumes using matplotlib.

    Parameters
    ----------
    data : 3D np.ndarray
        Volume to display.
    update_delay : int
        Minimum delay between events in milliseconds. Reduces lag
        by limiting the Limit update rate.
    **kwargs :
        Passed to first call of `SliceViewer.update`.
    """
    def __init__(
        self,
        data: np.ndarray,
        update_delay: int = 50,
        **kwargs,
    ):
        self.fig, self.ax = plt.subplots()
        self.data = data
        self.update_delay = update_delay / 1000

        self.max_vals = dict(zip('xyz', np.array(data.shape) - 1))
        self.labels = {
            'x': ('y', 'z'),
            'y': ('x', 'z'),
            'z': ('x', 'y'),
        }

        self.last_update = 0.0

        along = kwargs.get('along', 'x')
        init_max_val = self.max_vals[along]
        init_val = kwargs.get('index', int(init_max_val / 2))

        self.int_slider = IntSlider(value=init_val, min=0, max=init_max_val)
        self.radio_buttons = RadioButtons(options=('x', 'y', 'z'), value=along)

        self.im = self.ax.imshow(data[0])
        self.im.set_clim(vmin=data.min(), vmax=data.max())
        self.update(index=init_val, along=along)

    def get_slice(self, *, index: int, along: str):
        """Get slice associated with index along given axes."""
        if along == 'x':
            return self.data[:, :, index]
        elif along == 'y':
            return self.data[:, index, :]
        elif along == 'z':
            return self.data[index, ...]
        else:
            raise ValueError('`along` must be one of `x`,`y`,`z`')

    def update(self, index: int, along: str):
        """Update the image in place."""
        now = time.time()
        diff = now - self.last_update

        if diff < self.update_delay:
            return

        max_val = self.max_vals[along]

        xlabel, ylabel = self.labels[along]
        index = min(index, max_val)
        self.int_slider_max = max_val

        slice = self.get_slice(along=along, index=index)

        self.im.set_data(slice)
        self.ax.set_title(f'slice {index} along {along}')
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.fig.canvas.draw()

        self.last_update = time.time()

    def interact(self):
        """Call interactive `ipywidgets` widget."""
        interact(self.update, index=self.int_slider, along=self.radio_buttons)


def show_image(image, *, dpi=80, title=None):
    """Simple function to show an image using matplotlib.

    Parameters
    ----------
    image : 2D np.ndarray
        Image to display.
    dpi : int, optional
        DPI to render at.
    title : None, optional
        Title for the plot.
    """
    fig = plt.figure(dpi=dpi)
    plt.set_cmap('gray')

    ax = fig.add_subplot()
    ax.imshow(image, interpolation=None)

    if title:
        plt.title(title)

    ax.set_xlabel('x')
    ax.set_ylabel('y')

    return ax


@requires(condition=pygalmesh, message='requires pygalmesh')
def generate_mesh_from_binary_image(image: np.ndarray,
                                    h=(1.0, 1.0, 1.0),
                                    **kwargs):
    """Generate mesh from binary image using pygalmesh.

    Parameters
    ----------
    image : 2D np.ndarray
        Input image.
    h : tuple, optional
        Voxel size in x, y, z.
    **kwargs
        Keyword arguments passed to `pygalmesh.generate_from_array`.

    Returns
    -------
    meshio.Mesh
        Output mesh.
    """
    mesh = pygalmesh.generate_from_array(image, h, **kwargs)
    return mesh
