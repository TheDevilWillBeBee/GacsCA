"""Atomic, pickle-free scientific checkpoints with strict run identity checks."""
import json
import os
from pathlib import Path
import tempfile

import numpy as np


def save_checkpoint(path, metadata, arrays):
    path = Path(path)
    if "_metadata" in arrays or any(np.asarray(a).dtype.hasobject for a in arrays.values()):
        raise ValueError("checkpoint arrays must be numeric and cannot use _metadata")
    encoded = json.dumps(metadata, sort_keys=True, allow_nan=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", suffix=".tmp", delete=False) as f:
            temporary = Path(f.name)
            np.savez_compressed(f, _metadata=np.array(encoded), **arrays)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def load_checkpoint(path, identity):
    with np.load(path, allow_pickle=False) as data:
        metadata = json.loads(str(data["_metadata"]))
        if metadata.get("identity") != identity:
            raise ValueError("checkpoint identity mismatch: parameters, code, or binary changed")
        arrays = {k: data[k].copy() for k in data.files if k != "_metadata"}
    return metadata, arrays
