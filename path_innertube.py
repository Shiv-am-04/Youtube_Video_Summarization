import pytube
from pytube import innertube

# Save the original constructor of Innertube
original_init = innertube.InnerTube.__init__

# Define a patched version of the constructor that forces the client to 'WEB'
def patched_init(self, *args, **kwargs):
    # Change the client to 'WEB'
    kwargs['client'] = 'WEB'
    # Call the original constructor
    original_init(self, *args, **kwargs)

# Apply the patch to the Innertube class
innertube.InnerTube.__init__ = patched_init
