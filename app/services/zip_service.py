import os
import shutil
from fastapi import HTTPException

class ZipService:
    @staticmethod
    def zip_directory(directory_path: str, output_zip_path: str) -> str:
        if not os.path.isdir(directory_path):
            raise HTTPException(status_code=400, detail=f"Directory {directory_path} not found.")
        
        # Remove the zip extension if it exists in the output path
        if output_zip_path.endswith(".zip"):
            output_zip_path = output_zip_path[:-4]

        try:
            # Create a zip file of the directory
            shutil.make_archive(output_zip_path, 'zip', directory_path)
            return f"{output_zip_path}.zip"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to zip directory: {str(e)}")
