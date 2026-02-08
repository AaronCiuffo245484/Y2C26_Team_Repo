import xml.etree.ElementTree as ET
import sys
from pathlib import Path


def extract_root_lengths(rsml_file):
    """
    Extract root lengths from an RSML file.
    
    Parameters:
    -----------
    rsml_file : str
        Path to the RSML file
    
    Returns:
    --------
    list of dict
        Each dict contains 'root_id', 'label', and 'length_mm'
    """
    tree = ET.parse(rsml_file)
    root_elem = tree.getroot()
    
    results = []
    
    # Find all plant elements
    for plant in root_elem.findall('.//plant'):
        # Find all root elements within this plant
        for root in plant.findall('.//root'):
            root_id = root.get('ID')
            label = root.get('label')
            
            # Find the length property (in cm)
            length_elem = root.find('.//properties/length')
            
            if length_elem is not None:
                length_cm = float(length_elem.text)
                length_mm = length_cm * 10  # Convert cm to mm
                
                results.append({
                    'root_id': root_id,
                    'label': label,
                    'length_mm': length_mm
                })
    
    return results


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python extract_root_lengths.py <rsml_file>")
        sys.exit(1)
    
    # Get the input file path from command line
    input_file = Path(sys.argv[1])
    
    # Check if file exists
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    # Check if file has .rsml extension
    if input_file.suffix.lower() != '.rsml':
        print(f"Warning: File does not have .rsml extension: {input_file}")
    
    # Extract root lengths
    results = extract_root_lengths(input_file)
    
    print(f"Found {len(results)} roots:")
    print()
    
    for root in results:
        print(f"Root: {root['label']}")
        print(f"  ID: {root['root_id']}")
        print(f"  Length: {root['length_mm']:.2f} mm")
        print()
    
    # Summary statistics
    if results:
        total_length = sum(r['length_mm'] for r in results)
        avg_length = total_length / len(results)
        print(f"Total length: {total_length:.2f} mm")
        print(f"Average length: {avg_length:.2f} mm")
    else:
        print("No roots found in file.")
