# YARRAK

import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

STEP_TO_SEMITONE = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}


def pitch_to_midi(note: ET.Element) -> int | None:
    pitch = note.find("pitch")

    if pitch is None:
        return None

    step = pitch.findtext("step")
    octave = pitch.findtext("octave")
    alter = pitch.findtext("alter")

    if step is None or octave is None:
        return None

    semitone = STEP_TO_SEMITONE[step]

    if alter is not None:
        semitone += int(float(alter))

    return (int(octave) + 1) * 12 + semitone


def is_note(element: ET.Element) -> bool:
    return element.tag == "note"


def is_rest(note: ET.Element) -> bool:
    return note.find("rest") is not None


def is_chord_note(note: ET.Element) -> bool:
    return note.find("chord") is not None


def remove_chord_marker(note: ET.Element) -> None:
    chord_marker = note.find("chord")

    if chord_marker is not None:
        note.remove(chord_marker)


def clean_measure(measure: ET.Element) -> None:
    children = list(measure)
    index = 0

    while index < len(children):
        note = children[index]

        if not is_note(note):
            index += 1
            continue

        if is_rest(note):
            note.set("print-object", "no")
            index += 1
            continue

        if is_chord_note(note):
            index += 1
            continue

        chord_notes = [note]
        next_index = index + 1

        while next_index < len(children):
            next_note = children[next_index]

            if is_note(next_note) and is_chord_note(next_note):
                chord_notes.append(next_note)
                next_index += 1
            else:
                break

        if len(chord_notes) > 1:
            pitched_notes = [
                chord_note
                for chord_note in chord_notes
                if pitch_to_midi(chord_note) is not None
            ]

            if pitched_notes:
                highest_note = max(pitched_notes, key=pitch_to_midi)
                remove_chord_marker(highest_note)

                for chord_note in chord_notes:
                    if chord_note is not highest_note:
                        measure.remove(chord_note)

        index = next_index


def clean_score_xml(xml_bytes: bytes) -> bytes:
    root = ET.fromstring(xml_bytes)

    for measure in root.findall(".//measure"):
        clean_measure(measure)

    ET.indent(root, space="  ")

    return ET.tostring(
        root,
        encoding="utf-8",
        xml_declaration=True,
    )


def find_main_xml_path(mxl_path: Path) -> str:
    with zipfile.ZipFile(mxl_path, "r") as mxl_file:
        container_xml = mxl_file.read("META-INF/container.xml")
        container = ET.fromstring(container_xml)
        rootfile = container.find(".//rootfile")

        if rootfile is None:
            raise RuntimeError("Rootfile could not be found in the MXL archive.")

        main_xml_path = rootfile.attrib.get("full-path")

        if not main_xml_path:
            raise RuntimeError("Rootfile path is missing from the MXL archive.")

        return main_xml_path


def clean_mxl(input_path: Path, output_path: Path) -> None:
    main_xml_path = find_main_xml_path(input_path)

    with zipfile.ZipFile(input_path, "r") as input_archive:
        files = {
            filename: input_archive.read(filename)
            for filename in input_archive.namelist()
        }

    files[main_xml_path] = clean_score_xml(files[main_xml_path])

    with zipfile.ZipFile(
            output_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
    ) as output_archive:
        for filename, data in files.items():
            output_archive.writestr(filename, data)


def clean_mxl_in_place(input_path: Path) -> None:
    temporary_path = input_path.with_name(
        f"{input_path.stem}.temporary.mxl"
    )

    backup_path = input_path.with_name(
        f"{input_path.stem}.backup.mxl"
    )

    try:
        if not backup_path.exists():
            shutil.copy2(input_path, backup_path)

        clean_mxl(input_path, temporary_path)
        temporary_path.replace(input_path)

        print(f"Cleaned: {input_path.name}")

    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def main() -> None:
    target_folder = Path(__file__).resolve().parent

    mxl_files = [
        path
        for path in target_folder.glob("*.mxl")
        if not path.name.endswith(".backup.mxl")
           and not path.name.endswith(".temporary.mxl")
    ]

    if not mxl_files:
        print("No MXL files were found.")
        return

    print(f"Found {len(mxl_files)} MXL file(s).\n")

    success_count = 0
    error_count = 0

    for mxl_file in mxl_files:
        try:
            clean_mxl_in_place(mxl_file)
            success_count += 1

        except Exception as error:
            print(f"Error — {mxl_file.name}: {error}")
            error_count += 1

    print("\nFinished.")
    print(f"Successful: {success_count}")
    print(f"Failed: {error_count}")


if __name__ == "__main__":
    main()
