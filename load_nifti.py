import sys
import os
import slicer
import vtk
import subprocess
from qt import QWidget, QPushButton, QVBoxLayout, QLabel, Qt

# === Input NIfTI File ===
if len(sys.argv) < 2:
    print("Usage: load_nifti.py <nifti_file>")
    sys.exit(1)

nifti_path = sys.argv[1]
print(f"📂 Loading NIfTI file: {nifti_path}")

# === Load NIfTI Volume ===
success, volumeNode = slicer.util.loadVolume(nifti_path, returnNode=True)
if not success:
    print("❌ Failed to load NIfTI file.")
    sys.exit(1)

print(f"✅ Loaded volume node: {volumeNode.GetName()}")
slicer.util.setSliceViewerLayers(background=volumeNode)

# === GUI Dialog ===
class SaveDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NIfTI Loaded")
        self.setGeometry(100, 100, 300, 100)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Window)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("NIfTI loaded into Slicer.\nClick below to export to Unity."))

        self.save_button = QPushButton("Save and Continue")
        self.save_button.clicked.connect(self.on_save)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.show()

    def on_save(self):
        save_and_continue()
        self.close()

# === Export to OBJ (Surface Model) ===
def save_and_continue():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    obj_folder = os.path.join(script_dir, "Obj_files")
    os.makedirs(obj_folder, exist_ok=True)
    save_path = os.path.join(obj_folder, "nifti_volume.obj")

    segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", "NiftiSegmentation")
    segmentationNode.CreateDefaultDisplayNodes()

    slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(volumeNode, segmentationNode)
    segmentationNode.CreateClosedSurfaceRepresentation()

    slicer.modules.segmentations.logic().ExportAllSegmentsToModels(segmentationNode, 0)

    allModelNodes = slicer.util.getNodesByClass("vtkMRMLModelNode")
    exportable = [n for n in allModelNodes if "Segment" in n.GetName()]

    append_filter = vtk.vtkAppendPolyData()
    for node in exportable:
        slicer.vtkSlicerTransformLogic().hardenTransform(node)
        poly_data = node.GetPolyData()
        if poly_data:
            append_filter.AddInputData(poly_data)
    append_filter.Update()

    merged_model = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "Merged_Model")
    merged_model.SetAndObservePolyData(append_filter.GetOutput())

    display_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelDisplayNode")
    merged_model.SetAndObserveDisplayNodeID(display_node.GetID())
    display_node.SetVisibility(True)
    display_node.SetColor(0.8, 0.3, 0.3)
    display_node.SetOpacity(0.8)

    slicer.util.saveNode(merged_model, save_path)
    print(f"✅ Saved 3D model as {save_path}")
    open_unity_project(save_path)

# === Unity Integration ===
def open_unity_project(save_path):
    unity_executable = r"C:\Program Files\Unity\Hub\Editor\2022.3.15f1\Editor\Unity.exe"
    project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Unity", "FYP_Testing")
    execute_method = "ImportObj.ImportObjFile"
    cmd = f'"{unity_executable}" -projectPath "{project_path}" -executeMethod {execute_method} --filePath "{save_path}"'
    print(f"🚀 Launching Unity: {cmd}")
    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print(f"❌ Unity launch failed: {e}")

SaveDialog()
