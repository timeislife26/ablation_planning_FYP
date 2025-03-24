import subprocess
import os
import sys


def Start_Slicer(tumor_data):
    slicer_executable = r"C:\Program Files\slicer.org\Slicer 5.8.0\Slicer.exe"
    if os.path.exists(slicer_executable):
        try:
            print("3D Slicer is starting...")
            tumor_script_path = r"create_tumors.py"

            subprocess.Popen([
                slicer_executable,
                "--no-splash",
                "--python-script", tumor_script_path,
                tumor_data  # Pass as a single argument
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



def main():
    method = sys.argv[1]
    if method == "create":
        tumor_data = sys.argv[2]
        Start_Slicer(tumor_data)
    elif method == "dicom":
        folder_path = sys.argv[2]
        Start_Slicer_DICOM(folder_path)
    else:
        file_path = sys.argv[2]
        Start_Slicer_Import(file_path)




if __name__ == "__main__":
    main()
