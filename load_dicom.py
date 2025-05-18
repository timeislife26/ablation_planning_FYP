import sys
import os
import slicer
import vtk
import subprocess
from DICOMLib import DICOMUtils
from qt import QWidget, QPushButton, QVBoxLayout, QLabel, Qt, QTimer
import vtkSegmentationCorePython as vtkSegmentationCore

# 📂 Input: DICOM folder path from argument
dicom_folder = sys.argv[1]
print(f"📂 Importing DICOM folder: {dicom_folder}")

# 📁 Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
obj_output_dir = os.path.join(script_dir, "Obj_files")
os.makedirs(obj_output_dir, exist_ok=True)
unity_project_path = os.path.join(script_dir, "Unity", "FYP_Testing")
unity_executable = r"C:\Program Files\Unity\Hub\Editor\2022.3.15f1\Editor\Unity.exe"
obj_path = os.path.join(obj_output_dir, "RIDER_Tumor.obj")

# 📦 Initialize DICOM database
dicomDatabaseDir = os.path.join(slicer.app.temporaryPath, "DICOM")
os.makedirs(dicomDatabaseDir, exist_ok=True)
slicer.dicomDatabase.initializeDatabase(dicomDatabaseDir)

# ⏳ Step 1: Import DICOM and wait
def import_and_process_dicom():
    try:
        with DICOMUtils.TemporaryDICOMDatabase(dicomDatabaseDir) as db:
            DICOMUtils.importDicom(dicom_folder, db)
            patientUIDs = db.patients()
            if not patientUIDs:
                print("❌ No patients found.")
                return

            for patientUID in patientUIDs:
                for study in db.studiesForPatient(patientUID):
                    for series in db.seriesForStudy(study):
                        DICOMUtils.loadSeriesByUID([series])

        print("✅ DICOM import complete.")
        QTimer.singleShot(1000, export_tumor_segment_to_model)

    except Exception as e:
        print(f"❌ Failed to import DICOM: {e}")

# ⏳ Step 2: Export tumor segment as 3D model
def export_tumor_segment_to_model():
    segmentation_nodes = slicer.util.getNodesByClass("vtkMRMLSegmentationNode")
    found = False

    append_filter = vtk.vtkAppendPolyData()

    for seg_node in segmentation_nodes:
        segment_ids = vtkSegmentationCore.vtkSegmentation.GetSegmentIDs(seg_node.GetSegmentation())
        for seg_id in segment_ids:
            seg = seg_node.GetSegmentation().GetSegment(seg_id)
            seg_name = seg.GetName().lower()
            if any(keyword in seg_name for keyword in ["tumor", "lesion", "gtv"]):
                print(f"🎯 Exporting segment: {seg_name}")

                temp_seg_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", "TempTumorSeg")
                temp_seg_node.GetSegmentation().AddSegment(seg)
                temp_seg_node.CreateClosedSurfaceRepresentation()

                slicer.modules.segmentations.logic().ExportVisibleSegmentsToModels(temp_seg_node)

                models = slicer.util.getNodesByClass("vtkMRMLModelNode")
                for model_node in models:
                    if model_node.GetName().startswith("Segment_"):
                        slicer.vtkSlicerTransformLogic().hardenTransform(model_node)
                        poly_data = model_node.GetPolyData()
                        if poly_data:
                            append_filter.AddInputData(poly_data)
                            found = True

    if not found:
        print("⚠️ No tumor segment found in any segmentation node.")
        return

    append_filter.Update()

    merged_model = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "MergedTumor")
    merged_model.SetAndObservePolyData(append_filter.GetOutput())

    display_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelDisplayNode")
    merged_model.SetAndObserveDisplayNodeID(display_node.GetID())
    display_node.SetColor(0.8, 0.2, 0.2)
    display_node.SetOpacity(0.9)

    success = slicer.util.saveNode(merged_model, obj_path)
    if success:
        print(f"✅ Saved tumor OBJ to: {obj_path}")
        SaveDialog(obj_path)
    else:
        print("❌ Failed to save OBJ.")

# 🚀 Launch Unity
def open_unity_project(obj_path):
    execute_method = "ImportObj.ImportObjFile"
    cmd = f'"{unity_executable}" -projectPath "{unity_project_path}" -executeMethod {execute_method} --filePath "{obj_path}"'
    print(f"🚀 Launching Unity: {cmd}")
    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print(f"❌ Unity launch failed: {e}")

# 🖼️ GUI prompt
class SaveDialog(QWidget):
    def __init__(self, obj_path):
        super().__init__()
        self.obj_path = obj_path
        self.setWindowTitle("Save and Continue")
        self.setGeometry(100, 100, 300, 100)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Window)

        layout = QVBoxLayout()
        label = QLabel("Tumor model created.\nClick to launch Unity.")
        layout.addWidget(label)

        self.save_button = QPushButton("Open in Unity")
        self.save_button.clicked.connect(self.on_save)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.show()

    def on_save(self):
        open_unity_project(self.obj_path)
        self.close()

# ⏱️ Start
QTimer.singleShot(1000, import_and_process_dicom)
