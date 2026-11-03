import json

def make_unique(list_chars):
    return [c for id, c in enumerate(list_chars) if c not in list_chars[:id]]

def export_vocab(txt_file, outpath):
    with open(txt_file, "r") as f:
        i = 0
        vocab = []
        for line in f:
            extend_vocab = [c for c in line.strip() if c not in vocab]
            vocab.extend(extend_vocab)
            i += 1
            if i % 1000 == 0:
                print(f"Processed {i} lines")
    
    with open(outpath, "w") as f:
        for c in vocab:
            f.write(c + "\n")



def load_vocab(txt_file):
    with open(txt_file, "r") as f:
        return sum([list(line.strip()) for line in f], [])

def compare_vocab(txt_1, txt_2, outpath=None):
    vocab_1 = load_vocab(txt_1)
    vocab_2 = load_vocab(txt_2)
    print(f"Vocab 1: {len(vocab_1)}")
    print(f"Vocab 2: {len(vocab_2)}")

    # search for missing characters in vocab_2
    missing_chars = []
    for char in vocab_1:
        if char not in vocab_2:
            missing_chars.append(char)
    
    print(f"Missing characters: {len(missing_chars)}")

    # search for redundant characters in vocab_2
    redundant_chars = []
    for char in vocab_2:
        if char not in vocab_1:
            redundant_chars.append(char)
    
    print(f"Redundant characters: {len(redundant_chars)}")

    if not outpath:
        return dict(
            missing_chars=missing_chars,
            redundant_chars=redundant_chars
        )
    else:
        # dump in json file
        with open(outpath, "w") as f:
            json.dump(dict(
                missing_chars=missing_chars,
                redundant_chars=redundant_chars
            ), f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # export_vocab("assets/insurance.txt", "assets/vocab_insurance.txt")
    # compare_vocab("assets/failure_cases.txt", "assets/vocab_New_Cinnamon_ocr_24.07.txt", outpath="vocab_diff_ocrv3.json")
    import unicodedata
    text = [
        "μ",
        "η",
        "◿",
        "～",
        "✓",
        "₁",
        "₂",
        "₃",
        "€",
        "〠",
        "＜",
        "＞",
        "◼",
        "≅",
        "£",
        "‰",
        "≦"
    ]
    for c in text:
        print(c, unicodedata.normalize("NFKC", c))
