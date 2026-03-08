# Model weights (required)

This repository does **not** ship the pretrained model weights because they are large.
To run dALPS, download the two files below and place them **in this folder** (`models/`).

## 1) Download links (Google Drive)

### (A) Slice-selection CNN (Keras/TensorFlow)
- Required filename: `dALPS_CNN.h5`
- Share link: https://drive.google.com/file/d/1fLJC8nL0eCQ6wmfbLbaH6CLW62bDl2j0/view?usp=sharing
- File ID: `1fLJC8nL0eCQ6wmfbLbaH6CLW62bDl2j0`
- Direct download (sometimes works better for scripts): `https://drive.google.com/uc?export=download&id=1fLJC8nL0eCQ6wmfbLbaH6CLW62bDl2j0`

### (B) ROI detector (YOLOv5)
- Required filename: `dALPS_YoloV5.pt`
- Share link: https://drive.google.com/file/d/1eYUkZOSPJxc_vJgT7OiWbpHyycMejQKW/view?usp=sharing
- File ID: `1eYUkZOSPJxc_vJgT7OiWbpHyycMejQKW`
- Direct download (sometimes works better for scripts): `https://drive.google.com/uc?export=download&id=1eYUkZOSPJxc_vJgT7OiWbpHyycMejQKW`

> **Access note:** the links must have Google Drive sharing set to **“Anyone with the link can view/download”**.
> If users can open the preview but cannot download, ensure the owner did not disable “Viewers can download/print/copy”.

## 2) Expected directory structure

After downloading, your project should look like:

```text
dALPS/
  models/
    dALPS_CNN.h5
    dALPS_YoloV5.pt
    README.md
```

**Important:** dALPS expects the filenames to match **exactly** as above.

## 3) Download from the command line (optional)

If you want a one-liner download (Linux/macOS/WSL), you can use `gdown`:

```bash
pip install -U gdown
mkdir -p models
gdown --fuzzy "https://drive.google.com/file/d/1fLJC8nL0eCQ6wmfbLbaH6CLW62bDl2j0/view?usp=sharing" -O models/dALPS_CNN.h5
gdown --fuzzy "https://drive.google.com/file/d/1eYUkZOSPJxc_vJgT7OiWbpHyycMejQKW/view?usp=sharing" -O models/dALPS_YoloV5.pt
```

If your environment blocks `gdown`, download via browser and move the files into `models/`.

## 4) License / usage

These weights are provided for **research use**. If you redistribute them, please:
- confirm you have permission to share them,
- state the license explicitly,
- document training data provenance and any IRB/consent constraints (if applicable).

For software citation, see the main `README.md` (and `CITATION.cff`).

