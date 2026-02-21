import zipfile
import os

def create_submission_zip():
    # Files and directories to include
    include_files = [
        'app.py',
        'utils.py',
        'requirements.txt',
        'README.md',
        'PROJECT_REPORT.md',
        'DEPLOYMENT.md',
        'VIVA_SCRIPT.md'
    ]
    
    include_dirs = ['assets', 'data']
    
    zip_name = 'SmartResumeMatcher_Submission.zip'
    
    print(f"Creating {zip_name}...")
    
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add individual files
            for file in include_files:
                if os.path.exists(file):
                    print(f"  Adding {file}")
                    zipf.write(file)
                else:
                    print(f"  Warning: {file} not found!")
            
            # Add directories
            for directory in include_dirs:
                if os.path.exists(directory):
                    print(f"  Adding folder {directory}")
                    for root, _, files in os.walk(directory):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, start='.')
                            zipf.write(file_path, arcname)
                            
        print(f"\nSuccessfully created {zip_name}!")
        print("You can submit this file for your project.")
        
    except Exception as e:
        print(f"Error creating zip: {e}")

if __name__ == "__main__":
    create_submission_zip()
