import json, glob, os

def update_site_data():
    data = {
        'docs': {},
        'claims': []
    }

    # Load all rendered markdown docs
    for p in sorted(glob.glob('output/*.md')):
        fn = os.path.basename(p)
        with open(p, 'r', encoding='utf-8') as f:
            data['docs'][fn] = f.read()

    # Load all atomic claims
    with open('ledger/claims.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data['claims'].append(json.loads(line.strip()))

    # Write to site/data.json
    os.makedirs('site', exist_ok=True)
    with open('site/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Data site berhasil diperbarui: {len(data['docs'])} dokumen dan {len(data['claims'])} klaim atomik.")

if __name__ == '__main__':
    update_site_data()
