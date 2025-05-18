import subprocess
import os
import sys


def Start_Slicer(model_name,tumor_data):
    slicer_executable = r"C:\Program Files\slicer.org\Slicer 5.8.0\Slicer.exe"
    if os.path.exists(slicer_executable):
        try:
            print("3D Slicer is starting...")
            tumor_script_path = r"create_tumors.py"

            subprocess.Popen([
                slicer_executable,
                "--no-splash",
                "--python-script", tumor_script_path,
                model_name + "~" + tumor_data
            ])
        except Exception as e:
            print(f"Error while launching 3D Slicer: {e}")
    else:
        print(f"Slicer executable not found at {slicer_executable}")

def Start_Slicer_Import(file_path):
    slicer_executable = r"C:\Program Files\slicer.org\Slicer 5.8.0\Slicer.exe"
    if os.path.exists(slicer_executable):
        try:
            print("3D Slicer is attempting import...")
            tumor_script_path = r"load_tumour.py"

            subprocess.Popen([
                slicer_executable,
                "--no-splash",
                "--python-script", tumor_script_path,
                file_path
            ])
        except Exception as e:
            print(f"Error while launching 3D Slicer: {e}")
    else:
        print(f"Slicer executable not found at {slicer_executable}")

def Start_Slicer_DICOM(folder_path):
    slicer_executable = r"C:\Program Files\slicer.org\Slicer 5.8.0\Slicer.exe"
    if os.path.exists(slicer_executable):
        try:
            print("3D Slicer is loading DICOM folder...")
            dicom_script = r"load_dicom.py"

            subprocess.Popen([
                slicer_executable,
                "--no-splash",
                "--python-script", dicom_script,
                folder_path
            ])
        except Exception as e:
            print(f"Error while launching 3D Slicer: {e}")
    else:
        print(f"Slicer executable not found at {slicer_executable}")

def Start_Slicer_Nifti(nifti_path):
    import os

    slicer_executable = r"C:\Program Files\slicer.org\Slicer 5.8.0\Slicer.exe"

    if os.path.isdir(nifti_path):
        subprocess.Popen([
            slicer_executable,
            "--no-splash",
            "--python-script", "load_nifti.py",
            "--",
            "--folder", nifti_path
        ])
    else:
        subprocess.Popen([
            slicer_executable,
            "--no-splash",
            "--python-script", "load_nifti.py",
            "--",
            "--file", nifti_path
        ])




def main():
    method = sys.argv[1]
    if method == "create":
        model_name = sys.argv[2]
        tumor_data = sys.argv[3]
        Start_Slicer(model_name, tumor_data)
    elif method == "dicom":
        folder_path = sys.argv[2]
        Start_Slicer_DICOM(folder_path)
    elif method == "nifti":
        nifti_path = sys.argv[2]
        Start_Slicer_Nifti(nifti_path)

    else:
        file_path = sys.argv[2]
        Start_Slicer_Import(file_path)




if __name__ == "__main__":
    main()
