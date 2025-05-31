import requests

protein_name = "LGR4"
url = "https://rest.uniprot.org/uniprotkb/search"
params = {
    "query": f"gene:{protein_name} AND organism_id:9606 AND reviewed:true AND fragment:false",
    "format": "fasta",
    "size": 1
}

response = requests.get(url, params=params)

if response.status_code == 200 and response.text.strip():
    fasta_data = response.text.strip()
    print("FASTAデータの生のレスポンス：\n", fasta_data)

    lines = fasta_data.split('\n')
    sequence = ''.join(lines[1:])

    print("\n取得したアミノ酸シーケンス（連結後）：")
    print(sequence)
    print(f"\n取得したシーケンスの長さ: {len(sequence)}")
else:
    print("データ取得失敗")
