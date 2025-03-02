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


def main():
    if len(sys.argv) < 2:
        sys.exit("Error: Please provide tumor specifications.")

    tumor_data = sys.argv[1]  # The entire tumor data string
    Start_Slicer(tumor_data)


if __name__ == "__main__":
    main()
