#!/usr/bin/env python3
"""
Script para limpar e preparar os dados do YouTube para análise de hate speech
Mantém apenas os dados úteis e padroniza o formato
"""

import pandas as pd
from datetime import datetime

def clean_youtube_data():
    """Limpa e prepara os dados do YouTube para análise"""
    
    # Caminho para o arquivo do YouTube
    youtube_file = "clean-annotated-data/youtube/youtube.csv"
    
    print("📺 Carregando dados do YouTube...")
    
    try:
        # Ler o CSV
        df = pd.read_csv(youtube_file)
        print(f"📊 Total de registros carregados: {len(df):,}")
        
        # Verificar colunas disponíveis
        print(f"📋 Colunas disponíveis: {list(df.columns)}")
        
        # Verificar se tem a coluna 'comentario'
        if 'comentario' not in df.columns:
            print("❌ Coluna 'comentario' não encontrada!")
            return None
        
        # Filtrar apenas comentários não vazios
        print("🧹 Limpando dados...")
        df_clean = df[df['comentario'].notna() & (df['comentario'].str.strip() != '')].copy()
        print(f"✅ Comentários válidos após limpeza: {len(df_clean):,}")
        
        # Renomear coluna para padronizar
        df_clean = df_clean.rename(columns={'comentario': 'text'})
        
        # Adicionar ID único
        df_clean['id'] = range(1, len(df_clean) + 1)
        
        # Selecionar colunas úteis
        useful_columns = ['id', 'text', 'titulo_video', 'data', 'likes_comentario', 'autor_handle']
        available_columns = [col for col in useful_columns if col in df_clean.columns]
        
        df_clean = df_clean[available_columns].copy()
        
        # Adicionar coluna de origem
        df_clean['source_platform'] = 'youtube'
        
        # Salvar arquivo limpo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"clean-annotated-data/youtube_limpo_{timestamp}.csv"
        
        df_clean.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"💾 Arquivo limpo salvo: {output_file}")
        print(f"📋 Colunas finais: {list(df_clean.columns)}")
        
        # Estatísticas finais
        print(f"\n📈 Estatísticas finais:")
        print(f"   - Total de comentários: {len(df_clean):,}")
        print(f"   - Comentários com autor: {df_clean['autor_handle'].notna().sum():,}")
        print(f"   - Comentários com likes: {df_clean['likes_comentario'].notna().sum():,}")
        print(f"   - Comentários com data: {df_clean['data'].notna().sum():,}")
        print(f"   - Vídeos únicos: {df_clean['titulo_video'].nunique():,}")
        
        # Amostra dos dados
        print(f"\n📝 Amostra dos dados:")
        for i, row in df_clean.head(3).iterrows():
            text_preview = row['text'][:100] + "..." if len(row['text']) > 100 else row['text']
            print(f"   {i+1}. {text_preview}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Erro ao processar dados do YouTube: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 Iniciando limpeza dos dados do YouTube...")
    output_file = clean_youtube_data()
    if output_file:
        print(f"✅ Limpeza concluída! Arquivo: {output_file}")
    else:
        print("❌ Falha na limpeza dos dados do YouTube")
