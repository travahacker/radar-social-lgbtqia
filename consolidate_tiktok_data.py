#!/usr/bin/env python3
"""
Script para consolidar todos os arquivos CSV do TikTok em uma única planilha limpa
Mantém apenas os dados úteis para análise de hate speech
"""

import pandas as pd
import os
import glob
from datetime import datetime

def consolidate_tiktok_data():
    """Consolida todos os arquivos CSV do TikTok em uma planilha única limpa"""
    
    # Caminho para os arquivos do TikTok
    tiktok_dir = "clean-annotated-data/tiktok"
    
    # Buscar todos os arquivos CSV
    csv_files = glob.glob(os.path.join(tiktok_dir, "tiktok_*_comments.csv"))
    print(f"📱 Encontrados {len(csv_files)} arquivos do TikTok")
    
    # Lista para armazenar todos os DataFrames
    all_dataframes = []
    
    # Processar cada arquivo
    for i, file_path in enumerate(csv_files, 1):
        try:
            print(f"📂 Processando arquivo {i}/{len(csv_files)}: {os.path.basename(file_path)}")
            
            # Ler o CSV
            df = pd.read_csv(file_path)
            
            # Verificar se tem a coluna 'text'
            if 'text' not in df.columns:
                print(f"⚠️  Arquivo {file_path} não tem coluna 'text', pulando...")
                continue
            
            # Filtrar apenas comentários não vazios
            df_clean = df[df['text'].notna() & (df['text'].str.strip() != '')].copy()
            
            # Manter apenas colunas úteis
            useful_columns = ['text', 'author_handle', 'author_name', 'like_count_visible', 'timestamp_visible', 'video_id']
            available_columns = [col for col in useful_columns if col in df_clean.columns]
            
            df_clean = df_clean[available_columns].copy()
            
            # Adicionar coluna de origem
            df_clean['source_file'] = os.path.basename(file_path)
            
            # Adicionar à lista
            all_dataframes.append(df_clean)
            
            print(f"✅ {len(df_clean)} comentários válidos extraídos")
            
        except Exception as e:
            print(f"❌ Erro ao processar {file_path}: {str(e)}")
            continue
    
    if not all_dataframes:
        print("❌ Nenhum arquivo foi processado com sucesso!")
        return
    
    # Consolidar todos os DataFrames
    print("🔄 Consolidando todos os dados...")
    consolidated_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Remover duplicatas baseadas no texto
    print("🧹 Removendo duplicatas...")
    initial_count = len(consolidated_df)
    consolidated_df = consolidated_df.drop_duplicates(subset=['text'], keep='first')
    final_count = len(consolidated_df)
    duplicates_removed = initial_count - final_count
    
    print(f"📊 Estatísticas de consolidação:")
    print(f"   - Total inicial: {initial_count:,} comentários")
    print(f"   - Duplicatas removidas: {duplicates_removed:,}")
    print(f"   - Total final: {final_count:,} comentários únicos")
    
    # Adicionar ID único
    consolidated_df['id'] = range(1, len(consolidated_df) + 1)
    
    # Reordenar colunas
    column_order = ['id', 'text', 'author_handle', 'author_name', 'like_count_visible', 'timestamp_visible', 'video_id', 'source_file']
    available_columns = [col for col in column_order if col in consolidated_df.columns]
    consolidated_df = consolidated_df[available_columns]
    
    # Salvar arquivo consolidado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"clean-annotated-data/tiktok_consolidado_limpo_{timestamp}.csv"
    
    consolidated_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"💾 Arquivo consolidado salvo: {output_file}")
    print(f"📋 Colunas: {list(consolidated_df.columns)}")
    
    # Estatísticas finais
    print(f"\n📈 Estatísticas finais:")
    print(f"   - Total de comentários: {len(consolidated_df):,}")
    print(f"   - Comentários com autor: {consolidated_df['author_handle'].notna().sum():,}")
    print(f"   - Comentários com likes: {consolidated_df['like_count_visible'].notna().sum():,}")
    print(f"   - Comentários com timestamp: {consolidated_df['timestamp_visible'].notna().sum():,}")
    
    # Amostra dos dados
    print(f"\n📝 Amostra dos dados:")
    for i, row in consolidated_df.head(3).iterrows():
        text_preview = row['text'][:100] + "..." if len(row['text']) > 100 else row['text']
        print(f"   {i+1}. {text_preview}")
    
    return output_file

if __name__ == "__main__":
    print("🚀 Iniciando consolidação dos dados do TikTok...")
    output_file = consolidate_tiktok_data()
    print(f"✅ Consolidação concluída! Arquivo: {output_file}")
