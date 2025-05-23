import sys
import os
import slicer
import subprocess
import vtk
from DICOMLib import DICOMUtils
from qt import QWidget, QPushButton, QVBoxLayout, QLabel, Qt, QTimer
import vtkSegmentationCorePython as vtkSegmentationCore

# Input
dicom_folder = sys.argv[1]
model_name = sys.argv[2] if len(sys.argv) > 2 else "TumorModel"

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
obj_output_dir = os.path.join(script_dir, "Obj_files")
os.makedirs(obj_output_dir, exist_ok=True)
unity_project_path = os.path.join(script_dir, "Unity", "FYP_Testing")
unity_executable = r"C:\Program Files\Unity\Hub\Editor\2022.3.15f1\Editor\Unity.exe" # Path to Unity exe file. Change if needed

# DICOM DB init
dicomDatabaseDir = os.path.join(slicer.app.temporaryPath, "DICOM")
os.makedirs(dicomDatabaseDir, exist_ok=True)
slicer.dicomDatabase.initializeDatabase(dicomDatabaseDir)

# Step 1: Load DICOM and schedule export
def import_and_process_dicom():
    try:
        with DICOMUtils.TemporaryDICOMDatabase(dicomDatabaseDir) as db:
            DICOMUtils.importDicom(dicom_folder, db)
            for patientUID in db.patients():
                for study in db.studiesForPatient(patientUID):
                    for series in db.seriesForStudy(study):
                        DICOMUtils.loadSeriesByUID([series])
        QTimer.singleShot(1000, export_segmentation_to_obj)
    except Exception as e:
        print(f"DICOM load failed: {e}")

# Step 2: Export first valid segment to centered OBJ
def export_segmentation_to_obj():
    seg_nodes = slicer.util.getNodesByClass("vtkMRMLSegmentationNode")
    if not seg_nodes:
        print("No segmentation nodes found.")
        return

    for seg_node in seg_nodes:
        print(f"Exporting segmentation node: {seg_node.GetName()}")
        seg_node.CreateClosedSurfaceRepresentation()

        segment_ids = vtkSegmentationCore.vtkSegmentation.GetSegmentIDs(seg_node.GetSegmentation())
        if not segment_ids:
            print("No segments found.")
            continue

        for seg_id in segment_ids:
            segment_name = seg_node.GetSegmentation().GetSegment(seg_id).GetName()
            print(f"Processing segment: {segment_name}")

            temp_seg = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", f"TempSeg_{segment_name}")
            temp_seg.CreateDefaultDisplayNodes()

            success = temp_seg.GetSegmentation().CopySegmentFromSegmentation(
                seg_node.GetSegmentation(), seg_id)
            if not success:
                print(f"Failed to copy segment: {segment_name}")
                continue

            temp_seg.CreateClosedSurfaceRepresentation()
            if not temp_seg.GetSegmentation().ContainsRepresentation("Closed surface"):
                print(f"Segment '{segment_name}' has no closed surface representation.")
                slicer.mrmlScene.RemoveNode(temp_seg)
                continue

            temp_seg.GetDisplayNode().SetAllSegmentsVisibility(True)

            try:
                existing_models = set(m.GetID() for m in slicer.util.getNodesByClass("vtkMRMLModelNode"))
                slicer.modules.segmentations.logic().ExportVisibleSegmentsToModels(temp_seg, 0)
                print(f"Exported visible segments for '{segment_name}'")
            except Exception as e:
                print(f"ExportVisibleSegmentsToModels failed: {e}")
                slicer.mrmlScene.RemoveNode(temp_seg)
                continue

            new_models = [m for m in slicer.util.getNodesByClass("vtkMRMLModelNode")
                          if m.GetID() not in existing_models and m.GetPolyData()]

            if not new_models:
                print(f"No model found for segment: {segment_name}")
                slicer.mrmlScene.RemoveNode(temp_seg)
                continue

            model_node = new_models[0]
            print(f"Found new model node: {model_node.GetName()}")

            # Center the model at (0, 0, 0)
            center_filter = vtk.vtkCenterOfMass()
            center_filter.SetInputData(model_node.GetPolyData())
            center_filter.SetUseScalarsAsWeights(False)
            center_filter.Update()
            center = center_filter.GetCenter()
            print(f"Center of mass: {center}")

            transform = vtk.vtkTransform()
            transform.Translate(-center[0], -center[1], -center[2])

            transform_filter = vtk.vtkTransformPolyDataFilter()
            transform_filter.SetInputData(model_node.GetPolyData())
            transform_filter.SetTransform(transform)
            transform_filter.Update()

            model_node.SetAndObservePolyData(transform_filter.GetOutput())
            slicer.vtkSlicerTransformLogic().hardenTransform(model_node)

            obj_path = os.path.join(obj_output_dir, f"{segment_name}.obj")

            try:
                saved = slicer.util.saveNode(model_node, obj_path)
                if saved:
                    print(f"Saved .obj to: {obj_path}")
                    SaveDialog(obj_path)
                    return  # stop after first successful export
                else:
                    print(f"Failed to save OBJ for {segment_name}")
            except Exception as e:
                print(f"Error saving OBJ: {e}")

            slicer.mrmlScene.RemoveNode(temp_seg)
            slicer.mrmlScene.RemoveNode(model_node)

    print("No segment exported successfully.")

# Qt dialog to continue
class SaveDialog(QWidget):
    def __init__(self, obj_path):
        super().__init__()
        self.obj_path = obj_path
        self.setWindowTitle("Save and Continue")
        self.setGeometry(100, 100, 300, 100)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Window)

        layout = QVBoxLayout()
        label = QLabel("Segment exported to OBJ.\nClick below to open in Unity.")
        layout.addWidget(label)

        self.save_button = QPushButton("Open in Unity")
        self.save_button.clicked.connect(self.on_save)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.show()

    def on_save(self):
        open_unity_project(self.obj_path)
        self.close()

# Unity launcher
def open_unity_project(obj_path):
    execute_method = "ImportObj.ImportObjFile"
    cmd = f'"{unity_executable}" -projectPath "{unity_project_path}" -executeMethod {execute_method} --filePath "{obj_path}"'
    print(f"Launching Unity: {cmd}")
    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print(f"Unity launch failed: {e}")

# Run
QTimer.singleShot(1000, import_and_process_dicom)
