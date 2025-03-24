import sys
import os
import slicer

dicom_folder = sys.argv[1]
print(f"Importing DICOM folder: {dicom_folder}")

# Access the DICOM module
slicer.util.selectModule('DICOM')

# Initialize the DICOM database if needed
dicomDatabaseDir = os.path.join(slicer.app.temporaryPath, "DICOM")
slicer.dicomDatabase.initializeDatabase(dicomDatabaseDir)

# Import the DICOM folder
from DICOMLib import DICOMUtils

with DICOMUtils.TemporaryDICOMDatabase(dicomDatabaseDir) as db:
    DICOMUtils.importDicom(dicom_folder, db)

    patientUIDs = db.patients()
    if not patientUIDs:
        print("❌ No patients found in DICOM folder.")
        sys.exit(1)

    for patientUID in patientUIDs:
        studies = db.studiesForPatient(patientUID)
        for study in studies:
            seriesList = db.seriesForStudy(study)
            for seriesUID in seriesList:
                print(f"✅ Loading series: {seriesUID}")
                loadedNodes = DICOMUtils.loadSeriesByUID([seriesUID])
                if loadedNodes:
                    print(f"✅ Successfully loaded: {len(loadedNodes)} node(s)")
                else:
                    print("⚠️ Failed to load series.")
