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

# Zip filename
ZIP_FILE="NPEC_Time_Series_000.zip"

# Check if zip file exists
if [ ! -f "$ZIP_FILE" ]; then
    echo "Error: $ZIP_FILE not found in repo root"
    exit 1
fi

# Fetch latest from origin
echo "Fetching latest changes from origin..."
git fetch origin

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Check if branch is behind origin/main
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")

if [ "$BEHIND" -gt 0 ]; then
    echo ""
    echo "ERROR: Your branch is $BEHIND commit(s) behind origin/main"
    echo ""
    echo "Please run the following commands before unpacking:"
    echo "  git pull origin main"
    echo ""
    echo "If you're on a feature branch, you may want:"
    echo "  git merge origin/main"
    echo "  or"
    echo "  git rebase origin/main"
    echo ""
    exit 1
fi

# Warning about overwriting
echo ""
echo "WARNING: This will overwrite any existing image files in data/NPEC_Time_Series/ex_28_raw/"
echo ""
echo "Zip file: $ZIP_FILE"
echo "Size: $(du -h "$ZIP_FILE" | cut -f1)"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted"
    exit 0
fi

# Unpack zip file
echo "Unpacking $ZIP_FILE..."
unzip -o "$ZIP_FILE"

echo ""
echo "Successfully unpacked image files"
echo "You can now work with the data files in your repository"
