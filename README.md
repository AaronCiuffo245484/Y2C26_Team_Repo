# Y2C 25/26 Team Repo

## Image Data Management

Image files (.png, .jpg, .tiff, etc.) are too large to store in the git repository. Instead, they are distributed as zip files and unpacked locally. Data files (.rsml, .csv, .json, etc.) are version-controlled in git.

Follow the instructions below to obtain the base image set and unpack it into your repo. 

### Setup Instructions

#### 0. Clone the Repository

```bash
git clone https://github.com/AaronCiuffo245484/Y2C26_Team_Repo.git
cd Y2C26_Team_Repo
```

#### 1. Start with a clean repo

```bash
$ git fetch origin
$ git pull main
```

#### 2. Download Image Files

Download the image zip file from the shared storage:

[Inverted NPEC Time Series Data](https://edubuas-my.sharepoint.com/:u:/g/personal/245484_buas_nl/IQC_k6UEA0ocTY7TaPKk8DT6AVpWAa9JYPUMKto1Nl6ljYE?e=lu0Q1X)

Place the `NPEC_Time_Series_000.zip` file in the repository root directory: `Y2c26_Team_Repo/NPEC_Time_Series_000.zip`

#### 3. Unpack Images Using the Script 

This script will unpack the files into the appropriate locations and preserve data files that are managed by git.

From the repository root, run:

```bash
./utilities/unpack_image_zip.sh
```

The script will:

- Check that your branch is up-to-date with origin/main
- Warn you that existing image files will be overwritten
- Prompt for confirmation before proceeding

### Workflow Guidelines

#### Starting Work

Always begin with a clean, up-to-date branch:
```bash
git fetch origin
git pull origin main
```

Create a feature branch for your work:
```bash
git checkout -b feature/your-feature-name
```

#### Making Changes

1. Work with the image files locally (they are gitignored)
2. Add or modify data files (.rsml, .csv, .json, etc.)
3. Commit your data file changes:

```bash
git add data/
git commit -m "Add analysis results for experiment X"
```

#### Submitting Changes

Push your feature branch and create a pull request:

```bash
git push origin feature/your-feature-name
```

Then create a PR through the repository's web interface.

### Creating Image Zips (Maintainers Only)

If you need to create a new image zip file:

```bash
./utilities/create_image_zip.sh
```

This will create `NPEC_Time_Series_000.zip` containing all image files from `data/NPEC_Time_Series/ex_28_raw/`.

### Troubleshooting

#### "Your branch is X commits behind origin/main"

Run these commands before unpacking:
```bash
git pull origin main
```

If you're on a feature branch:
```bash
git merge origin/main
```

#### "NPEC_Time_Series_000.zip not found"

Ensure the zip file is in the repository root directory, not in a subdirectory.

#### Script Permission Denied

Make the scripts executable:
```bash
chmod +x utilities/create_image_zip.sh
chmod +x utilities/unpack_image_zip.sh
```