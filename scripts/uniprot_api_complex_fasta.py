import pandas as pd
import requests
import time
import os

# FASTA取得関数
def fetch_uniprot_sequence(protein_name):
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"gene:{protein_name} AND organism_id:9606 AND reviewed:true AND fragment:false",
        "format": "fasta",
        "size": 1
    }
    response = requests.get(url, params=params)

    # Humanのタンパク質が無ければ、他の生物のタンパク質を取得
    if response.status_code == 200 and response.text.strip():
        lines = response.text.strip().split('\n')
        sequence = ''.join(lines[1:])
        return sequence
    else:
        # Humanのタンパク質が見つからない場合、全生物で再検索
        params["query"] = protein_name
        response = requests.get(url, params=params)
        if response.status_code == 200 and response.text:
            lines = response.text.strip().split('\n')
            sequence = ''.join(lines[1:])
            return sequence
        else:
            return None

# メイン関数
def create_fasta_from_excel(gpcr_file=None, ligand_file=None, output_dir="output_fasta_files"):
    os.makedirs(output_dir, exist_ok=True)

    gpcr_df = pd.read_excel(gpcr_file) if gpcr_file else None
    ligand_df = pd.read_excel(ligand_file) if ligand_file else None

    total = len(gpcr_df) if gpcr_df is not None else len(ligand_df)
    
    failed_proteins = []

    for i in range(total):
        gpcr_name = gpcr_df.iloc[i, 0] if gpcr_df is not None else None
        ligand_name = ligand_df.iloc[i, 0] if ligand_df is not None else None

        if gpcr_name and ligand_name:
            gpcr_seq = fetch_uniprot_sequence(gpcr_name)
            ligand_seq = fetch_uniprot_sequence(ligand_name)
            filename_suffix = "_suspect" if gpcr_seq and len(gpcr_seq) < 300 else ""
            output_file = os.path.join(output_dir, f"{gpcr_name}_{ligand_name}{filename_suffix}.fasta")
            with open(output_file, 'w') as fasta_file:
                fasta_file.write(f">A|protein|\n{gpcr_seq if gpcr_seq else '取得失敗'}\n")
                fasta_file.write(f">B|protein|\n{ligand_seq if ligand_seq else '取得失敗'}\n")
                
            if not gpcr_seq:
                failed_proteins.append(gpcr_name)
            if not ligand_seq:
                failed_proteins.append(ligand_name)

        elif gpcr_name:
            gpcr_seq = fetch_uniprot_sequence(gpcr_name)
            filename_suffix = "_suspect" if gpcr_seq and len(gpcr_seq) < 350 else ""
            output_file = os.path.join(output_dir, f"{gpcr_name}{filename_suffix}.fasta")
            with open(output_file, 'w') as fasta_file:
                fasta_file.write(f">A|protein|\n{gpcr_seq if gpcr_seq else '取得失敗'}\n")
                
            if not gpcr_seq:
                failed_proteins.append(gpcr_name)

        elif ligand_name:
            ligand_seq = fetch_uniprot_sequence(ligand_name)
            output_file = os.path.join(output_dir, f"{ligand_name}.fasta")
            with open(output_file, 'w') as fasta_file:
                fasta_file.write(f">A|protein|\n{ligand_seq if ligand_seq else '取得失敗'}\n")
                
            if not ligand_seq:
                failed_proteins.append(ligand_name)

        # 100件ごとに3分待機
        if (i + 1) % 100 == 0:
            print(f"{i + 1}件取得完了。3分待機します...")
            time.sleep(180)

    if failed_proteins:
        print("以下のタンパク質のシーケンス取得に失敗しました:")
        for protein in failed_proteins:
            print(protein)
            
    print("全てのfastaファイルの作成が問題なく完了しました")

# 使用例
if __name__ == "__main__":
    gpcr_excel = "C:\\wisteria_data\\push\\GPCR_name.xlsx"        # GPCRエクセルファイルのパス
    ligand_excel = "C:\\wisteria_data\\push\\Ligand_name.xlsx"    # リガンドエクセルファイルのパス
    output_directory = "C:\\wisteria_data\\push" # 出力ディレクトリ

    create_fasta_from_excel(gpcr_excel, ligand_excel, output_directory)
