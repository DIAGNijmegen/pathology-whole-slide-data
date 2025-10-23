# image_processing/add_spacing_metadata.py

import argparse
import os
import numpy as np
import tifffile
from pathlib import Path
from wholeslidedata.image.wholeslideimage import WholeSlideImage

def add_spacing_metadata(input_path: str, output_folder: str, spacing: float = 0.5, tmp_folder: str = None):
    """Fast metadata update using in-place TIFF tag overwriting."""
    os.makedirs(output_folder, exist_ok=True)
    
    output_path = os.path.join(output_folder, os.path.basename(input_path))
    
    # Add filesystem diagnostics
    print(f"Input path: {input_path}")
    print(f"Output path: {output_path}")
    print(f"Input exists: {os.path.exists(input_path)}")
    print(f"Output folder writable: {os.access(output_folder, os.W_OK)}")
    
    # Check if output file already exists
    if os.path.exists(output_path):
        print(f"Output file already exists, skipping: {output_path}")
        return
    
    # Convert spacing to resolution (microns per pixel to pixels per inch)
    # spacing is in microns per pixel, convert to pixels per inch
    pixels_per_inch = 10000 / spacing
    
    # Get actual downsample information from the image
    actual_downsamples = []
    try:
        import openslide
        with openslide.OpenSlide(input_path) as slide:
            actual_downsamples = list(slide.level_downsamples)
            print(f"Detected downsamples from OpenSlide: {actual_downsamples}")
    except Exception as e:
        print(f"Could not read downsample info from OpenSlide: {e}")
        print("Will determine downsamples from TIFF structure...")
        actual_downsamples = None  # Will be determined from actual TIFF pages
    
    try:
        # Create a temporary file in the tmp_folder for in-place editing
        temp_dir = tmp_folder if tmp_folder else os.path.dirname(output_path)
        
        # Create temporary file with same name pattern in tmp folder
        temp_filename = os.path.basename(output_path)
        temp_output_path = os.path.join(temp_dir, f"tmp_{temp_filename}")
        
        # Copy the file to the tmp location
        import shutil
        shutil.copyfile(input_path, temp_output_path)
        print(f"Copied file to: {temp_output_path}")

        # Open the temporary file for in-place editing
        with tifffile.TiffFile(temp_output_path, mode='r+') as tif:
            num_pages = len(tif.pages)
            print(f"Updating metadata for {num_pages} pages...")
            
            # If we couldn't get downsamples from OpenSlide, calculate from page dimensions
            if actual_downsamples is None or len(actual_downsamples) != num_pages:
                print("Calculating downsamples from page dimensions...")
                actual_downsamples = []
                base_width = tif.pages[0].shape[1] if tif.pages else 1
                
                for page in tif.pages:
                    page_width = page.shape[1]
                    downsample = base_width / page_width if page_width > 0 else 1.0
                    actual_downsamples.append(downsample)
                
                print(f"Calculated downsamples: {actual_downsamples}")
            
            # Ensure we have exactly the right number of downsample values
            if len(actual_downsamples) != num_pages:
                print(f"Warning: Mismatch between pages ({num_pages}) and downsamples ({len(actual_downsamples)})")
                # Pad or truncate as needed
                while len(actual_downsamples) < num_pages:
                    last_downsample = actual_downsamples[-1] if actual_downsamples else 1.0
                    actual_downsamples.append(last_downsample * 2)  # Approximate next level
                actual_downsamples = actual_downsamples[:num_pages]  # Truncate if too many

            # Update resolution tags for all pages
            for page_idx, page in enumerate(tif.pages):
                # Use actual downsample for this page
                downsample = actual_downsamples[page_idx] if page_idx < len(actual_downsamples) else (2**page_idx)
                effective_spacing = spacing * downsample
                
                # Calculate resolution for this page based on downsample
                # As downsample increases, resolution (pixels per inch) decreases
                page_pixels_per_inch = pixels_per_inch / downsample
                
                print(f"  Page {page_idx}: downsample={downsample:.3f}, effective_spacing={effective_spacing:.3f} μm/px, resolution={page_pixels_per_inch:.1f} ppi")
                
                # Update XResolution and YResolution with page-specific resolution
                if 'XResolution' in page.tags:
                    page.tags['XResolution'].overwrite((int(page_pixels_per_inch), 1))
                    
                if 'YResolution' in page.tags:
                    page.tags['YResolution'].overwrite((int(page_pixels_per_inch), 1))
                
                # Update ResolutionUnit
                if 'ResolutionUnit' in page.tags:
                    page.tags['ResolutionUnit'].overwrite(3) # 3 = centimeters
                
            print(f"Updated XResolution/YResolution for all pages based on downsample factors")
            
        # Move the updated file from temp folder to final output location
        print(f"Moving updated file from temp to final location...")
        print(f"Source: {temp_output_path}")
        print(f"Destination: {output_path}")
        
        # Move the updated file to final location
        shutil.copyfile(temp_output_path, output_path)
        os.remove(temp_output_path)  # Clean up temp file after copying
        print(f"Successfully moved updated file to: {output_path}")
                    
    except PermissionError as e:
        print(f"Permission error when updating TIFF metadata: {e}")
        print(f"Check file permissions and filesystem mount options")
        # Clean up temp file if it exists
        if 'temp_output_path' in locals() and os.path.exists(temp_output_path):
            print(f"Cleaning up temporary file: {temp_output_path}")
            os.remove(temp_output_path)
        raise
    except OSError as e:
        print(f"OS error when updating TIFF metadata: {e}")
        print(f"This might be a cross-filesystem or mount issue")
        # Clean up temp file if it exists
        if 'temp_output_path' in locals() and os.path.exists(temp_output_path):
            print(f"Cleaning up temporary file: {temp_output_path}")
            os.remove(temp_output_path)
        raise
    except Exception as e:
        print(f"Unexpected error when updating TIFF metadata: {e}")
        print(f"Error type: {type(e).__name__}")
        # Clean up temp file if it exists
        if 'temp_output_path' in locals() and os.path.exists(temp_output_path):
            print(f"Cleaning up temporary file: {temp_output_path}")
            os.remove(temp_output_path)
        raise
    
    print(f"Saved: {output_path}")

def _parse_args():
    # create argument parser
    argument_parser = argparse.ArgumentParser(description="Add image spacing")
    argument_parser.add_argument("-i", "--input_data", required=True)
    argument_parser.add_argument("-s", "--spacing", required=False, default=0.5, type=float)
    argument_parser.add_argument("-t", "--tmp_folder", required=False)
    argument_parser.add_argument("-o", "--output_folder", required=False)
    argument_parser.add_argument("-e", "--extension", required=False)

    args = vars(argument_parser.parse_args())

    args["input_data"] = Path(args["input_data"])

    if args["tmp_folder"] is None:
        args["tmp_folder"] = Path("/tmp/")
    else:
        args["tmp_folder"] = Path(args["tmp_folder"])

    if args["output_folder"] is not None:
        args["output_folder"] = Path(args["output_folder"])

    return args


def main():
    args = _parse_args()
    input_data = args["input_data"]
    output_folder = args["output_folder"]
    tmp_folder = args["tmp_folder"]
    spacing = args["spacing"]
    extension = args["extension"]

    if not input_data.exists():
        raise ValueError(f"Input data {input_data} does not exists")

    image_paths = None
    if os.path.isdir(input_data):
        if output_folder is None:
            output_folder = input_data / f"spacing_{str(spacing).replace('.', '-')}"
        if extension is None:
            raise ValueError(f"Input data {input_data} is a folder, but extension is None")
        image_paths = list(input_data.glob("*." + extension.replace(".", "")))

    if os.path.isfile(input_data):
        if output_folder is None:
            output_folder = input_data.parent / "spacing_added"
        image_paths = [input_data]

    output_folder.mkdir(parents=True, exist_ok=True)

    for image_path in image_paths:
        # Preserve the original file extension
        output_path = output_folder / image_path.name

        if output_path.exists():
            print(f"Skipping: {output_path} already exists.")
            continue

        print(f"Processing: {image_path}")
        try:
            # Try the fast in-place method first
            add_spacing_metadata(str(image_path), str(output_folder), spacing, str(tmp_folder) if tmp_folder else None)
        except Exception as e:
            print(f"ERROR: can not process image: {image_path} - {e}")
            continue

        print("Done!")


# Keep CLI option for backwards compatibility
if __name__ == "__main__":
    import sys
    # Check if using old CLI format for backwards compatibility
    if len(sys.argv) == 3 and not any(arg.startswith('-') for arg in sys.argv[1:]):
        print("Using legacy CLI format. Consider using: python add_image_spacing.py -i <input> -o <output>")
        add_spacing_metadata(sys.argv[1], sys.argv[2])
    else:
        main()
