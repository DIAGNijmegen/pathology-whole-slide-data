import sys
import os
import argparse
from pathlib import Path

def inspect_image_metadata(image_path):
    """Inspect image metadata using multiple backends for comprehensive information."""
    print(f"Analyzing image: {image_path}")
    print("=" * 80)
    
    # Try OpenSlide first
    try:
        import openslide
        print("\n--- OpenSlide Properties ---")
        slide = openslide.OpenSlide(image_path)
        
        # Basic slide info
        print(f"Dimensions: {slide.dimensions} (width x height)")
        print(f"Level count: {slide.level_count}")
        print(f"Level dimensions: {slide.level_dimensions}")
        print(f"Level downsamples: {slide.level_downsamples}")
        
        # Extract spacing information
        mpp_x = slide.properties.get("aperio.MPP") or slide.properties.get("openslide.mpp-x")
        mpp_y = slide.properties.get("aperio.MPP") or slide.properties.get("openslide.mpp-y")
        
        if mpp_x and mpp_y:
            print(f"\nSpacing information:")
            print(f"  Microns per pixel (X): {mpp_x}")
            print(f"  Microns per pixel (Y): {mpp_y}")
        else:
            print("\nNo spacing metadata found in OpenSlide properties")
        
        # Print all properties
        print("\nAll OpenSlide properties:")
        for k, v in sorted(slide.properties.items()):
            print(f"  {k}: {v}")
        
        slide.close()
        
    except Exception as e:
        print(f"OpenSlide failed: {e}")
    
    # Try WholeSlideData
    try:
        from wholeslidedata.image.wholeslideimage import WholeSlideImage
        print("\n--- WholeSlideData Information ---")
        
        wsi = WholeSlideImage(image_path, backend='asap')
        print(f"Spacings: {wsi.spacings}")
        print(f"Shapes: {wsi.shapes}")
        print(f"Levels: {wsi.level_count}")
        
    except Exception as e:
        print(f"WholeSlideData failed: {e}")
    
    # Try tifffile for TIFF-specific metadata
    try:
        import tifffile
        print("\n--- TIFF Metadata (tifffile) ---")
        
        with tifffile.TiffFile(image_path) as tif:
            print(f"Number of pages: {len(tif.pages)}")
            
            # First page info
            page = tif.pages[0]
            print(f"First page dimensions: {page.shape}")
            print(f"First page dtype: {page.dtype}")
            print(f"Compression: {page.compression}")
            print(f"Photometric: {page.photometric}")
            
            # Resolution info
            if hasattr(page, 'tags'):
                if 'XResolution' in page.tags:
                    x_res = page.tags['XResolution'].value
                    print(f"XResolution: {x_res}")
                if 'YResolution' in page.tags:
                    y_res = page.tags['YResolution'].value
                    print(f"YResolution: {y_res}")
                if 'ResolutionUnit' in page.tags:
                    res_unit = page.tags['ResolutionUnit'].value
                    unit_names = {1: 'NONE', 2: 'INCH', 3: 'CENTIMETER'}
                    unit_name = unit_names.get(res_unit, f'UNKNOWN({res_unit})')
                    print(f"ResolutionUnit: {res_unit} ({unit_name})")
            
            # Print all TIFF tags from first page
            print(f"\nAll TIFF tags (page 0):")
            for tag in page.tags.values():
                try:
                    if len(str(tag.value)) > 100:  # Truncate very long values
                        value_str = str(tag.value)[:100] + "..."
                    else:
                        value_str = str(tag.value)
                    print(f"  {tag.name} ({tag.code}): {value_str}")
                except:
                    print(f"  {tag.name} ({tag.code}): <could not read value>")
            
            # Show info for additional pages if they exist
            if len(tif.pages) > 1:
                print(f"\nAdditional pages (pyramid levels):")
                for i, page in enumerate(tif.pages[1:6], 1):  # Show up to 5 additional levels
                    print(f"  Page {i}: {page.shape}, compression: {page.compression}")
                if len(tif.pages) > 6:
                    print(f"  ... and {len(tif.pages) - 6} more pages")

            print("Calculating decompression size...")
            arr = tif.asarray()  # fully decompresses the image
            uncompressed_bytes = arr.nbytes
            print(f"Uncompressed size: {uncompressed_bytes / 1e9:.2f} GB")
                    
    except Exception as e:
        print(f"TiffFile failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Inspect whole slide image metadata and spacing information")
    parser.add_argument("input_data", help="Path to the input image file")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_data)
    
    if not input_path.exists():
        print(f"Error: File {input_path} does not exist")
        sys.exit(1)
    
    if not input_path.is_file():
        print(f"Error: {input_path} is not a file")
        sys.exit(1)
    
    inspect_image_metadata(str(input_path))

if __name__ == "__main__":
    main()