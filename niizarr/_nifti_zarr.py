import zarr
from nibabel import Nifti1Header, Nifti2Header


class NIfTIZarr:
    def __init__(self, ):
        self.nih: Nifti1Header | Nifti2Header = None
        self.data: zarr.Group = None
        self.path = None

        pass

    @classmethod
    def open(cls, path):
        self = cls()
        self.path = path
        self.data = zarr.open(path)
        self.nih = self._load_nifti_header()
        return self

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def __repr__(self):
        return f"<NIfTIZarr: {self.path}>"
