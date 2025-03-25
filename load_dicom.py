import sys
import os
import slicer
import vtk
from DICOMLib import DICOMUtils
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

# Create editor node & widget
segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentEditorNode')
segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
segmentEditorWidget.setSegmentationNode(segmentationNode)
segmentEditorWidget.setSourceVolumeNode(bestVolumeNode)

# Apply Threshold effect
segmentEditorWidget.setActiveEffectByName("Threshold")
effect = segmentEditorWidget.activeEffect()
effect.setParameter("MinimumThreshold", "100")  # 🔧 Adjust based on scan
effect.setParameter("MaximumThreshold", "300")
effect.self().onApply()
segmentEditorWidget = None

print("✅ Threshold segmentation complete.")

# 🧊 Step 3: Generate 3D surface
segmentationNode.CreateClosedSurfaceRepresentation()

# 🧱 Step 4: Export to 3D models
shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
segmentationItemID = shNode.GetItemByDataNode(segmentationNode)
slicer.modules.segmentations.logic().ExportAllSegmentsToModels(segmentationNode, segmentationItemID)

# 💾 Step 5: Save as STL or OBJ
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ExportedModels")
os.makedirs(output_dir, exist_ok=True)

modelNodes = slicer.util.getNodesByClass('vtkMRMLModelNode')
for modelNode in modelNodes:
    modelName = modelNode.GetName().replace(" ", "_")
    output_path = os.path.join(output_dir, f"{modelName}.stl")
    if slicer.util.saveNode(modelNode, output_path):
        print(f"✅ Saved model: {output_path}")
    else:
        print(f"⚠️ Failed to save model: {modelName}")

# 👀 Step 6: Visualize in viewer
slicer.util.setSliceViewerLayers(background=bestVolumeNode, label=segmentationNode)
print("✅ Done.")
