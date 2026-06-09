# MusicXML Flute Cleaner

A lightweight Python utility that simplifies compressed MusicXML (`.mxl`) files for monophonic flute practice.

I essentially came up with the idea after having to deal with messy piano notes. If you only want to use the notes for playing on the flute, then this project is for you.

The script processes every `.mxl` file in its own folder, replaces each chord with its highest note, hides rests from the printed score, and saves the cleaned result in place.

A backup of each original file is created automatically before any changes are made.

## What It Does

For each `.mxl` file:

* Finds the main MusicXML file inside the compressed MXL archive
* Replaces every chord with its highest-pitched note
* Removes the remaining notes from the chord
* Hides rests using `print-object="no"`
* Preserves the original MXL archive structure
* Creates a `.backup.mxl` copy before overwriting the original file

## Example

Before running the script:

```text
musicxml-flute-cleaner/
├── flute_cleaner.py
└── titlegold.mxl
```

After running the script:

```text
musicxml-flute-cleaner/
├── flute_cleaner.py
├── titlegold.mxl
└── titlegold.backup.mxl
```

`titlegold.mxl` contains the simplified score.
`titlegold.backup.mxl` contains the untouched original score.

## Requirements

* Python 3.10 or newer
* No third-party dependencies

## Usage

1. Download `flute_cleaner.py`.
2. Place the script in the same folder as the `.mxl` files you want to process.
3. Run:

```bash
python flute_cleaner.py
```

The script automatically processes every `.mxl` file in the folder.

## Using PyCharm

1. Open `flute_cleaner.py` in PyCharm.
2. Place your `.mxl` files in the same folder as the script.
3. Right-click inside the editor.
4. Select **Run 'flute_cleaner'**.

After the first run, you can use the green Run button in the toolbar.

## Notes

* Existing `.backup.mxl` files are never overwritten.
* Backup files are ignored during future runs.
* If one file fails, the script reports the error and continues processing the remaining files.
* Only compressed MusicXML files with the `.mxl` extension are processed.

## License

This project is available under the MIT License.
