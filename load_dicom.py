import sys
import os
import slicer
import vtk
import subprocess
from DICOMLib import DICOMUtils
from qt import QWidget, QPushButton, QVBoxLayout, QLabel, Qt
import vtkSegmentationCorePython as vtkSegmentationCore

# 📂 Step 1: Load DICOM folder
dicom_folder = sys.argv[1]
print(f"📂 Importing DICOM folder: {dicom_folder}")

dicomDatabaseDir = os.path.join(slicer.app.temporaryPath, "DICOM")
slicer.dicomDatabase.initializeDatabase(dicomDatabaseDir)

with DICOMUtils.TemporaryDICOMDatabase(dicomDatabaseDir) as db:
    DICOMUtils.importDicom(dicom_folder, db)
    patientUIDs = db.patients()
    if not patientUIDs:
        print("❌ No patients found.")
        sys.exit(1)

    bestVolumeNode = None
    maxSlices = 0

    for patientUID in patientUIDs:
        for study in db.studiesForPatient(patientUID):
            for series in db.seriesForStudy(study):
                loadedNodeRefs = DICOMUtils.loadSeriesByUID([series])
                for nodeRef in loadedNodeRefs:
                    try:
                        node = slicer.util.getNode(nodeRef)
                        if node and node.IsA("vtkMRMLScalarVolumeNode"):
                            dims = node.GetImageData().GetDimensions()
                            numSlices = dims[2]
                            print(f"📦 Loaded {node.GetName()} with {numSlices} slices")
                            if numSlices > maxSlices:
                                maxSlices = numSlices
                                bestVolumeNode = node
                    except Exception as e:
                        print(f"⚠️ Could not get node from {nodeRef}: {e}")

if not bestVolumeNode:
    print("❌ No suitable volume found.")
    sys.exit(1)

print(f"✅ Selected volume for segmentation: {bestVolumeNode.GetName()}")

# 🧠 Step 2: Auto-segmentation using Threshold
segmentationNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode', "AutoSegmentation")
segmentationNode.CreateDefaultDisplayNodes()
segmentationNode.GetSegmentation().AddEmptySegment("AutoSegment")

segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentEditorNode')
segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
segmentEditorWidget.setSegmentationNode(segmentationNode)
segmentEditorWidget.setSourceVolumeNode(bestVolumeNode)

segmentEditorWidget.setActiveEffectByName("Threshold")
effect = segmentEditorWidget.activeEffect()
effect.setParameter("MinimumThreshold", "100")  # Adjust as needed
effect.setParameter("MaximumThreshold", "300")
effect.self().onApply()
segmentEditorWidget = None

print("✅ Threshold segmentation complete.")

# 🧊 Step 3: Generate 3D surface
segmentationNode.CreateClosedSurfaceRepresentation()

# 👀 Optional visualization
slicer.util.setSliceViewerLayers(background=bestVolumeNode, label=segmentationNode)

# 🎛️ GUI: SaveDialog for user confirmation
class SaveDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Save and Continue")
        self.setGeometry(100, 100, 300, 100)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Window)

        layout = QVBoxLayout()
        label = QLabel("Segmentation is ready.\nClick below when ready to save and export to Unity.")
        layout.addWidget(label)

        self.save_button = QPushButton("Save and Continue")
        self.save_button.clicked.connect(self.on_save)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.show()

    def on_save(self):
        save_and_continue()
        self.close()

# 💾 Save + Export to Unity
def save_and_continue():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    obj_folder = os.path.join(script_dir, "Obj_files")
    os.makedirs(obj_folder, exist_ok=True)
    save_path = os.path.join(obj_folder, "segmented_tumor.obj")

    # ✅ Export segments to models and capture them immediately
    segmentationLogic = slicer.modules.segmentations.logic()
    segmentationLogic.ExportAllSegmentsToModels(segmentationNode, 0)

    # Get all model nodes created after export
    allModelNodes = slicer.util.getNodesByClass("vtkMRMLModelNode")
    segmentationModelNodes = [node for node in allModelNodes if node.GetName().startswith("Segment_")]

    if not segmentationModelNodes:
        print("❌ No segmentation models found.")
        return

    # Merge them
    append_filter = vtk.vtkAppendPolyData()
    for node in segmentationModelNodes:
        slicer.vtkSlicerTransformLogic().hardenTransform(node)
        poly_data = node.GetPolyData()
        if poly_data:
            append_filter.AddInputData(poly_data)

    append_filter.Update()

    merged_model_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "Merged_Segmentation_Model")
    # Center the model geometry at (0, 0, 0)
    centered = vtk.vtkCenterOfMass()
    centered.SetInputData(append_filter.GetOutput())
    centered.SetUseScalarsAsWeights(False)
    centered.Update()
    com = centered.GetCenter()

    transform = vtk.vtkTransform()
    transform.Translate(-com[0], -com[1], -com[2])

    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetTransform(transform)
    transform_filter.SetInputData(append_filter.GetOutput())
    transform_filter.Update()

    # Set the centered polydata on the model node
    merged_model_node.SetAndObservePolyData(transform_filter.GetOutput())

    display_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelDisplayNode")
    merged_model_node.SetAndObserveDisplayNodeID(display_node.GetID())
    display_node.SetVisibility(True)

    success = slicer.util.saveNode(merged_model_node, save_path)
    if success:
        print(f"✅ Saved segmentation as {save_path}")
        open_unity_project(os.path.join(script_dir, "Unity", "FYP_Testing"), save_path)
    else:
        print("❌ Failed to save segmentation.")


# 🚀 Launch Unity
def open_unity_project(project_path, save_path):
    unity_executable = r"C:\Program Files\Unity\Hub\Editor\2022.3.15f1\Editor\Unity.exe"
    execute_method = "ImportObj.ImportObjFile"
    cmd = f'"{unity_executable}" -projectPath "{project_path}" -executeMethod {execute_method} --filePath "{save_path}"'
    print(f"🚀 Launching Unity: {cmd}")
    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print(f"❌ Unity launch failed: {e}")

# 🎛️ Show GUI to proceed when ready
SaveDialog()
