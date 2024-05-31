from dataclasses import dataclass
from pathlib import Path
import gzip
import struct
from io import BytesIO
from typing import Optional
from lxml import etree as ET

# List can be found at VADDR 0x8C9636C in the EBOOT
NAMES: dict[int, str] = {
    0x01: "————",
    0x02: "クレス",
    0x03: "チェスター",
    0x04: "ミント",
    0x05: "アーチェ",
    0x06: "すず",
    0x07: "ダオス",
    0x08: "スタン",
    0x09: "ルーティ",
    0x0A: "リオン",
    0x0B: "フィリア",
    0x0C: "ウッドロウ",
    0x0D: "リリス",
    0x0E: "コングマン",
    0x0F: "リッド",
    0x10: "ファラ",
    0x11: "キール",
    0x12: "チャット",
    0x13: "カイル",
    0x14: "リアラ",
    0x15: "ナナリー",
    0x16: "ハロルド",
    0x17: "バルバトス",
    0x18: "ロイド",
    0x19: "コレット",
    0x1A: "ジーニアス",
    0x1B: "リフィル",
    0x1C: "クラトス",
    0x1D: "ゼロス",
    0x1E: "プレセア",
    0x1F: "セルシウス",
    0x20: "ヴェイグ",
    0x21: "クレア",
    0x22: "ユージーン",
    0x23: "マオ",
    0x24: "アニー",
    0x25: "セネル",
    0x26: "クロエ",
    0x27: "ルーク",
    0x28: "ティア",
    0x29: "ガイ",
    0x2A: "ジェイド",
    0x2B: "アニス",
    0x2C: "アッシュ",
    0x2D: "カイウス",
    0x2E: "ルビア",
    0x2F: "ルカ",
    0x30: "イリア",
    0x31: "スパーダ",
    0x32: "カノンノ",
    0x33: "ユーリ",
    0x34: "エステル",
    0x35: "パニール",
    0x36: "ニアタ",
    0x37: "ジャニス",
    0x38: "助手",
    0x3B: "ゲーデ",
    0x3C: "ショー・コーロン",
    0x3D: "エコー・フラワー",
    0x3E: "ナディ構成員",
    0x3F: "ナディ構成員",
    0x40: "ナディ構成員",
    0x41: "ビクター",
    0x42: "傷ついた兵士",
    0x43: "青年",
    0x44: "男",
    0x46: "謎の男",
    0x47: "アニス？",
    0x48: "クロエ？",
    0x4E: "ファラ？",
    0x3A: "受付お姉さん",
    0x00: "パスカ・カノンノ",
}


@dataclass
class trEntry:
    jp_text: str
    en_text: str
    notes: str
    id: int
    status: str
    voice_id: Optional[int] = None
    speaker_id: Optional[int] = None


@dataclass
class rmXml:
    friend_name: Optional[str]
    names: list[trEntry]
    text: dict[str, list[trEntry]]


def makeNode(root: ET._Element, n: trEntry, id: int) -> ET._Element:
    entry = ET.SubElement(root, "Entry")

    # if n.offsets is not None:
    #     ET.SubElement(entry, "PointerOffset").text = ",".join(
    #         [str(x) for x in n.offsets]
    #     )
    # else:
    #     ET.SubElement(entry, "PointerOffset").text = None

    if n.voice_id is not None:
        ET.SubElement(entry, "VoiceId").text = n.voice_id

    ET.SubElement(entry, "JapaneseText").text = n.jp_text.replace("\r\n", "\n")
    ET.SubElement(entry, "EnglishText").text = n.en_text
    ET.SubElement(entry, "Notes").text = n.notes

    if n.speaker_id is not None:
        ET.SubElement(entry, "SpeakerId").text = str(n.speaker_id)

    ET.SubElement(entry, "Id").text = str(id)
    ET.SubElement(entry, "Status").text = n.status
    return entry


def makeXml(data: rmXml) -> bytes:
    root = ET.Element("SceneText")

    if data.friend_name is not None:
        ET.SubElement(root, "FriendlyName").text = data.friend_name

    names_node = ET.SubElement(root, "Speakers")
    ET.SubElement(names_node, "Section").text = "Speaker"
    for n in data.names:
        makeNode(names_node, n, n.id)

    for name, items in data.text.items():
        text_node = ET.SubElement(root, "Strings")
        ET.SubElement(text_node, "Section").text = name
        for n in items:
            makeNode(text_node, n, n.id)

    return ET.tostring(root, encoding="UTF-8", pretty_print=True)


def get_string_at(f, addr: int, encoding: str = "ascii") -> str:
    pos = f.tell()
    f.seek(addr)
    s = b""
    while True:
        c = f.read(1)
        if c == b"\x00":
            break
        else:
            s = s + c

    f.seek(pos)
    return s.decode(encoding)


def get_blob_at(f, addr: int, size: int) -> bytes:
    pos = f.tell()
    f.seek(addr)

    c = f.read(size)

    f.seek(pos)
    return c


def main() -> None:
    # face_folder = Path("0_disc/USRDIR/npc")
    face_folder = Path("0_disc/USRDIR/facechat")

    for file in face_folder.glob("*.arc"):
        with file.open("rb") as f:
            assert f.read(8) == b"EZBIND\x00\x00", "Not an EZBIND file!"
            file_count, alignment = struct.unpack("<II", f.read(8))

            for _ in range(file_count):
                name_offset, file_size, file_pos, hash = struct.unpack(
                    "<IIII", f.read(0x10)
                )
                name = get_string_at(f, name_offset)
                # print(get_blob_at(f, file_pos, file_size)[:8])
                if ".scr" not in name:
                    continue

                raw = gzip.decompress(get_blob_at(f, file_pos, file_size))
                # print("--------", file.as_posix(), "|", name, "--------")
                short_name = file.as_posix().replace("0_disc/USRDIR/", "")
                short_name = f'"{short_name}|{name}"'
                
                scr = BytesIO(raw)
                assert scr.read(8) == b"FaceChat", "Not a FaceChat file!"
                unk8, str_count, code_count, _ = struct.unpack(
                    "<hhhH", scr.read(0x8)
                )
                len_off = 0x10 + code_count * 2
                str_off = 0x10 + (code_count * 2) + (str_count * 2)
                lines = list()
                unrefs = dict()
                scr.seek(len_off)
                strs = struct.unpack(f"<{str_count}H", scr.read(str_count * 2))
                for i, s in enumerate(strs):
                    lines.append(get_string_at(scr, str_off + s, "euc-jp"))
                    unrefs[i] = lines[-1]

                scr.seek(0x10)
                names = dict()
                xml = rmXml(None, list(), {"Main Text": list(), "Unreferenced": list()})
                jump_marker = 0xFFFFFFFF
                while scr.tell() < len_off:
                    opcode = struct.unpack("<H", scr.read(2))[0]
                    p_count = (1 << (opcode & 3)) - 1
                    params = struct.unpack(f"<{p_count}H", scr.read(p_count * 2))
                    cmd_id = opcode >> 2
                    if cmd_id in (0xF, 0x1C):
                        if cmd_id == 0xF:
                            xml.text["Main Text"].append(trEntry(lines[params[2]], None, None, params[2], "To Do", None, params[1] + 1))
                            unrefs.pop(params[2], None)
                            names[params[1] + 1] = NAMES.get(params[1] + 1, f"<Name:{params[1] + 1:X}>")
                        elif cmd_id == 0x1C:
                            xml.text["Main Text"].append(trEntry(lines[params[0]], None, "Choice 1", params[0], "To Do", None, None))
                            xml.text["Main Text"].append(trEntry(lines[params[1]], None, "Choice 2", params[1], "To Do", None, None))
                            unrefs.pop(params[0], None)
                            unrefs.pop(params[1], None)
                            jump_marker = 0x10 + (params[2] * 2)
                        
                        if jump_marker < scr.tell():
                            jump_marker = 0xFFFFFFFF
                            xml.text["Main Text"][-1].notes = "Previous Choice 2 leads here"
                
                # Add names
                for id, nm in names.items():
                    xml.names.append(trEntry(nm, None, None, id, "To Do"))

                # Add unrefs
                for id, txt in unrefs.items():
                    xml.text["Unreferenced"].append(trEntry(txt, None, None, id, "To Do"))

                
                out = Path("./2_translated/facechat" + name)
                out = out.with_suffix(".xml")
                with out.open("wb") as o:
                    o.write(makeXml(xml))

if __name__ == "__main__":
    main()
