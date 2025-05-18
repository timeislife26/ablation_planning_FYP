import slicer
import os
import sys
import argparse

def load_nifti_volume(path):
    loaded_node = slicer.util.loadVolume(path)
    if loaded_node is None:
        raise RuntimeError(f"Failed to load volume: {path}")
    print(f"✅ Loaded volume: {path}")
    return loaded_node

def load_nifti_segmentation(path):
    loaded_node = slicer.util.loadLabelVolume(path)
    if loaded_node is None:
        raise RuntimeError(f"Failed to load segmentation: {path}")
    print(f"✅ Loaded segmentation: {path}")
    return loaded_node

def segment_to_model(segmentation_node):
    success, model_node = slicer.util.labelMapVolumeToModel(segmentation_node)
    if success:
        print("✅ Converted segmentation to model")
    else:
        raise RuntimeError("❌ Failed to convert segmentation to model")
    return model_node

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Single NIfTI file path")
    parser.add_argument("--folder", help="Folder with volume and segmentation")
    args = parser.parse_args()

    if args.file:
        load_nifti_volume(args.file)

    elif args.folder:
        files = os.listdir(args.folder)
        volume_file = next((f for f in files if f.startswith("volume-") and f.endswith(".nii")), None)
        seg_file = next((f for f in files if f.startswith("segmentation-") and f.endswith(".nii")), None)

        if not volume_file:
            raise FileNotFoundError("❌ No volume-*.nii file found in folder")

        volume_path = os.path.join(args.folder, volume_file)
        seg_path = os.path.join(args.folder, seg_file) if seg_file else None

        vol_node = load_nifti_volume(volume_path)

        if seg_path:
            seg_node = load_nifti_segmentation(seg_path)
            segment_to_model(seg_node)
        else:
            print("⚠️ No segmentation-*.nii found; only volume loaded.")

    else:
        raise ValueError("❌ Must specify either --file or --folder")

if __name__ == "__main__":
    main()
