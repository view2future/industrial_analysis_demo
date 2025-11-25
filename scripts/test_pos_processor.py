#!/usr/bin/env python3

from src.analysis.text_processor import TextProcessor
import json
from pathlib import Path
import os

def run_pos_processor_script():
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent.resolve() # scripts/ is one level down from root

    # Process test file
    processor = TextProcessor()
    
    # Construct absolute paths for input and output files
    input_file_path = project_root / "tests" / "fixtures" / "test_pos_removal.txt"
    output_file_path = project_root / "tests" / "fixtures" / "test_pos_removal_result.json"

    result = processor.analyze_file(str(input_file_path))

    if result is None:
        print("❌ Analysis failed")
        # Do not exit here, let the calling process handle it
        return False

    print('Key insights types:')
    for insight in result.get('key_insights', []):
        if isinstance(insight, dict):
            print(f'  - {insight.get("type", "N/A")}')

    # Save result
    with open(output_file_path, 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ Analysis completed and saved to {output_file_path}")
    return True

if __name__ == "__main__":
    if not run_pos_processor_script():
        # If run directly and analysis fails, exit with an error code
        exit(1)
