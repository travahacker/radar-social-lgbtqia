#!/usr/bin/env python3
"""
Script para atualizar o dataset com dados das três redes sociais (Instagram, TikTok, YouTube)
"""

import pandas as pd
import os
from datetime import datetime

def update_dataset_with_three_platforms():
    """Atualiza o dataset com dados das três redes sociais"""
    
    print("🔄 Atualizando dataset com dados das três redes sociais...")
    
    # Carregar dados das três plataformas
    datasets = {
        'Instagram': 'clean-annotated-data/export_1757023553205_limpa.csv',
        'TikTok': 'clean-annotated-data/tiktok_consolidado_limpo_20251016_181651.csv',
        'YouTube': 'clean-annotated-data/youtube_limpo_20251016_181656.csv'
    }
    
    # Colunas de texto para cada dataset
    text_columns = {
        'Instagram': 'Comment Text',
        'TikTok': 'text',
        'YouTube': 'text'
    }
    
    all_data = []
    
    for platform, file_path in datasets.items():
        print(f"📱 Processando {platform}...")
        
        try:
            # Carregar dados com separador correto
            if platform == 'Instagram':
                df = pd.read_csv(file_path, sep=';')
            else:
                df = pd.read_csv(file_path)
            
            text_col = text_columns[platform]
            
            # Preparar dados para o dataset
            for idx, row in df.iterrows():
                text = str(row[text_col])
                
                # Criar entrada do dataset
                entry = {
                    'id': f"{platform.lower()}_{idx+1}",
                    'text': text,
                    'platform': platform,
                    'source': 'clean_annotated_data',
                    'date_collected': datetime.now().strftime('%Y-%m-%d')
                }
                
                # Adicionar colunas específicas de cada plataforma
                if platform == 'Instagram':
                    entry.update({
                        'author_handle': row.get('Author Handle', ''),
                        'like_count': row.get('Like Count', ''),
                        'timestamp': row.get('Timestamp', '')
                    })
                elif platform == 'TikTok':
                    entry.update({
                        'author_handle': row.get('author_handle', ''),
                        'like_count_visible': row.get('like_count_visible', ''),
                        'timestamp_visible': row.get('timestamp_visible', ''),
                        'video_id': row.get('video_id', '')
                    })
                elif platform == 'YouTube':
                    entry.update({
                        'titulo_video': row.get('titulo_video', ''),
                        'data': row.get('data', ''),
                        'likes_comentario': row.get('likes_comentario', ''),
                        'autor_handle': row.get('autor_handle', '')
                    })
                
                all_data.append(entry)
            
            print(f"✅ {platform}: {len(df):,} comentários processados")
            
        except Exception as e:
            print(f"❌ Erro ao processar {platform}: {str(e)}")
            continue
    
    # Criar DataFrame consolidado
    consolidated_df = pd.DataFrame(all_data)
    
    # Salvar dataset atualizado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"datasets/dataset_three_platforms_{timestamp}.csv"
    
    # Criar diretório se não existir
    os.makedirs('datasets', exist_ok=True)
    
    consolidated_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\n📊 Dataset consolidado criado:")
    print(f"   - Arquivo: {output_file}")
    print(f"   - Total de comentários: {len(consolidated_df):,}")
    
    # Estatísticas por plataforma
    print(f"\n📱 Distribuição por plataforma:")
    platform_counts = consolidated_df['platform'].value_counts()
    for platform, count in platform_counts.items():
        print(f"   - {platform}: {count:,} comentários")
    
    # Salvar também versão limpa (apenas texto e ID)
    clean_df = consolidated_df[['id', 'text', 'platform']].copy()
    clean_file = f"datasets/dataset_three_platforms_clean_{timestamp}.csv"
    clean_df.to_csv(clean_file, index=False, encoding='utf-8')
    
    print(f"\n📄 Dataset limpo criado: {clean_file}")
    
    # Criar README para o dataset
    readme_content = f"""# Dataset Três Redes Sociais - {datetime.now().strftime('%d/%m/%Y')}

## 📊 Estatísticas

- **Total de comentários**: {len(consolidated_df):,}
- **Instagram**: {platform_counts.get('Instagram', 0):,} comentários
- **TikTok**: {platform_counts.get('TikTok', 0):,} comentários  
- **YouTube**: {platform_counts.get('YouTube', 0):,} comentários

## 📁 Arquivos

- `dataset_three_platforms_{timestamp}.csv`: Dataset completo com metadados
- `dataset_three_platforms_clean_{timestamp}.csv`: Dataset limpo (apenas texto e ID)

## 🔒 Privacidade

- Dados pessoais removidos
- IDs anonimizados
- Conformidade com LGPD/GDPR

## 🎯 Uso

Este dataset pode ser usado para:
- Treinamento de modelos de detecção de hate speech
- Análise de padrões por rede social
- Validação de sistemas existentes

## ⚠️ Aviso

Este dataset contém conteúdo sensível relacionado a discurso de ódio. Use com responsabilidade.
"""
    
    readme_file = f"datasets/README_three_platforms_{timestamp}.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📝 README criado: {readme_file}")
    
    return output_file, clean_file

if __name__ == "__main__":
    print("🚀 Iniciando atualização do dataset...")
    full_file, clean_file = update_dataset_with_three_platforms()
    if full_file:
        print(f"✅ Dataset atualizado com sucesso!")
        print(f"📁 Arquivos criados:")
        print(f"   - Completo: {full_file}")
        print(f"   - Limpo: {clean_file}")
    else:
        print("❌ Falha na atualização do dataset")
