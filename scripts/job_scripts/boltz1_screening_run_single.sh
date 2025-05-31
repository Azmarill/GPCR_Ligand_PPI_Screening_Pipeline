#!/bin/bash -l
#PJM -L rscgrp=share
#PJM -L gpu=4
#PJM -g gn46
#PJM -L elapse=8:00:00
#PJM -j
#PJM -o /work/gn46/n46001/research_projects/250530_Kato_screening/scripts/logs/boltz1_%j.log

module load cuda/12.2

#export CUDA_VISIBLE_DEVICES=0,1,2,3

# Conda activate Boltz-1 environment
CONDA_BASE=/work/04/gn46/share/conda/miniconda3
source "${CONDA_BASE}/etc/profile.d/conda.sh"
conda activate boltz1_env

# 作業ディレクトリをジョブごとに設定
RUN_DIR=/work/gn46/n46001/research_projects/250509_TGFα_screening/output/Adenine_output/batch_${BATCH_ID}
mkdir -p "$RUN_DIR" && cd "$RUN_DIR"

#重要！configが書き込まれる場所を指定しないと、$HOME下を勝手に指定してしまい、書き込み権限エラーが置きます
export XDG_CONFIG_HOME=$RUN_DIR/.config
mkdir -p $XDG_CONFIG_HOME

export TRITON_CACHE_DIR=$RUN_DIR/.triton_cache
mkdir -p $TRITON_CACHE_DIR

export BOLTZ_CACHE=$RUN_DIR/.boltz_cache
mkdir -p $BOLTZ_CACHE

export TORCH_HOME=$RUN_DIR/.torch
export XDG_CACHE_HOME=$RUN_DIR/.cache
mkdir -p $TORCH_HOME
mkdir -p $XDG_CACHE_HOME

#デバッグ用なのでコメントアウト可

#echo "BOLTZ_CACHE_DIR=$BOLTZ_CACHE_DIR"

# 入力FASTAファイルディレクトリ
INPUT_FASTA_DIR="/work/gn46/n46001/research_projects/250530_Kato_screening/input/"

#PJMが割り当てたGPUを配列として取得
#IFS=',' read -ra GPU_IDS <<< "$CUDA_VISIBLE_DEVICES"
#NUM_GPUS=${#GPU_IDS[@]}
#gpu_index=0

#インタラクティブ用なのでコメントアウト可
#echo "割り当てられたGPU番号: ${CUDA_VISIBLE_DEVICES}"
#nvidia-smi

# 出力ディレクトリ作成
OUTPUT_DIR="/work/gn46/n46001/research_projects/250530_Kato_screening/output_single/"
mkdir -p "$OUTPUT_DIR"

#GPUの枚数を規定
#NUM_GPUS=4

#GPU割り当てカウンタ
#gpu_index=0

# Boltz-1による構造予測（各FASTAファイルに対して処理）
#知り合いは、dirを指定すれば勝手に巡回してくれると言ってたけどなんか逆にめんどくさくてやってない
for fasta_file in "$INPUT_FASTA_DIR"/*.fasta; do
    filename=$(basename "$fasta_file" .fasta)

    if [ -d "$OUTPUT_DIR/$filename/boltz_results_${filename}" ]; then
        echo "Skipping $filename (already predicted)."
        continue
    fi

    #gpu=$((gpu_index % NUM_GPUS))gpu=${GPU_IDS[$gpu_index]}
    #echo "Processing $filename on GPU $gpu..."

    boltz predict "$fasta_file" \
        --use_msa_server \
        --recycling_steps 15 \
        --diffusion_samples 20 \
        --out_dir "$OUTPUT_DIR/$filename"

    #GPUインデックスを更新
    #gpu_index=$((gpu_index + 1))

    #if (( $(jobs -r -p | wc -l) >= NUM_GPUS )); then
        #wait -n
    #fi

done

#wait

conda deactivate
