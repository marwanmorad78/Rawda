# Image Optimization

The project automatically converts future uploaded images to WebP before
Django storage writes them.

## Profiles

| Image type | Maximum dimension | WebP quality |
| --- | ---: | ---: |
| Product primary and gallery | 800 px | 80 |
| Category cover | 1000 px | 85 |
| Company logo | 500 px | 85 |
| Promotion/banner | 1400 px | 80 |

EXIF rotation is applied before resizing. PNG transparency is preserved.

## PythonAnywhere Deployment

From a PythonAnywhere Bash console:

```bash
cd ~/Rawda
source .venv/bin/activate
pip install -r requirements.txt
python src/manage.py check --settings=config.settings.production
python src/manage.py migrate
```

Back up SQLite and uploaded media before converting existing files:

```bash
mkdir -p backups
python -c "import sqlite3; src=sqlite3.connect('db.sqlite3'); dst=sqlite3.connect('backups/db-before-images.sqlite3'); src.backup(dst); dst.close(); src.close()"
tar -czf "backups/media-before-images-$(date +%F-%H%M).tar.gz" src/media
```

Preview a small batch:

```bash
python src/manage.py optimize_images --dry-run --limit 50
```

Convert in batches that fit within the PythonAnywhere console time limit:

```bash
python src/manage.py optimize_images --limit 50
```

Run the same batch command again until the summary reports zero pending
records. Already-converted WebP records are excluded from later batches.

To process every remaining image in one run:

```bash
python src/manage.py optimize_images
```

On the PythonAnywhere **Web** tab, ensure the static-files mapping contains:

```text
URL:       /media/
Directory: /home/YOUR_USERNAME/Rawda/src/media
```

Use the actual absolute project path for your account. Reload the web app from
the Web tab after migration. No template changes are required because database
image paths are updated to the new WebP filenames.

## Command Behavior

- Processes database records with an iterator and opens one image at a time.
- Skips missing files safely.
- Continues after corrupt or unsupported files and logs each failure.
- Updates the database only after the WebP file is saved.
- Deletes the original file only after the database update succeeds.
- Supports `--dry-run` and a global `--limit`.
