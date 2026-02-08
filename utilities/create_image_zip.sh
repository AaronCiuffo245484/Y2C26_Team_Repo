#!/bin/bash

# Exit on error
set -e

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Get repo root
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# Check if data/ directory exists
if [ ! -d "data" ]; then
    echo "Error: data/ directory does not exist"
    exit 1
fi

# Create target directory if it doesn't exist
TARGET_DIR="data/NPEC_Time_Series/ex_28_raw"
if [ ! -d "$TARGET_DIR" ]; then
    echo "Creating directory: $TARGET_DIR"
    mkdir -p "$TARGET_DIR"
fi

# Output zip filename
ZIP_FILE="NPEC_Time_Series_000.zip"

# Find all image files (case-insensitive) and create zip
echo "Searching for image files in $TARGET_DIR..."

# Create temporary file list
TEMP_LIST=$(mktemp)

# Find image files (case-insensitive)
find "$TARGET_DIR" -type f \( \
    -iname "*.png" -o \
    -iname "*.jpg" -o \
    -iname "*.jpeg" -o \
    -iname "*.tiff" -o \
    -iname "*.tif" -o \
    -iname "*.bmp" -o \
    -iname "*.gif" -o \
    -iname "*.webp" \
\) > "$TEMP_LIST"

# Check if any files were found
FILE_COUNT=$(wc -l < "$TEMP_LIST")

if [ "$FILE_COUNT" -eq 0 ]; then
    echo "Warning: No image files found in $TARGET_DIR"
    rm "$TEMP_LIST"
    exit 1
fi

echo "Found $FILE_COUNT image file(s)"
echo "Creating $ZIP_FILE..."

# Create zip from file list, preserving directory structure
zip -q "$ZIP_FILE" -@ < "$TEMP_LIST"

# Cleanup
rm "$TEMP_LIST"

echo "Successfully created $ZIP_FILE"
echo "Size: $(du -h "$ZIP_FILE" | cut -f1)"
