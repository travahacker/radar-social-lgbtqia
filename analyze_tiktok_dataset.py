#!/usr/bin/env python3
"""
Script para analisar o dataset do TikTok usando o sistema Space otimizado
"""

import pandas as pd
import sys
import os
from datetime import datetime
from app_space_version import predict_hate_speech

def analyze_tiktok_dataset():
    """Analisa o dataset do TikTok com o sistema Space otimizado"""
    
    # Encontrar o arquivo mais recente do TikTok
    tiktok_files = [f for f in os.listdir('clean-annotated-data') if f.startswith('tiktok_consolidado_limpo_')]
    if not tiktok_files:
        print("❌ Nenhum arquivo do TikTok encontrado!")
        return
    
    # Pegar o mais recente
    latest_file = sorted(tiktok_files)[-1]
    input_file = f"clean-annotated-data/{latest_file}"
    
    print(f"📱 Analisando dataset do TikTok: {input_file}")
    
    try:
        # Carregar dados
        df = pd.read_csv(input_file)
        print(f"📊 Total de comentários: {len(df):,}")
        
        # Verificar se tem coluna 'text'
        if 'text' not in df.columns:
            print("❌ Coluna 'text' não encontrada!")
            return
        
        # Lista para armazenar resultados
        results = []
        
        print("🔍 Iniciando análise com sistema Space otimizado...")
        
        # Processar cada comentário
        for idx, row in df.iterrows():
            if idx % 100 == 0:
                print(f"📈 Processando comentário {idx+1:,}/{len(df):,}")
            
            text = str(row['text'])
            
            try:
                # Usar sistema Space otimizado
                result = predict_hate_speech(text)
                
                # Adicionar resultado
                results.append({
                    'id': row.get('id', idx + 1),
                    'text': text,
                    'text_length': len(text),
                    'text_features': f"Length: {len(text)}, Words: {len(text.split())}, Has_emoji: {'emoji' in text.lower()}",
                    'predicted_label': 'HATE' if result['is_hate'] else 'NÃO-HATE',
                    'method': result['method'],
                    'specialized_class': result['specialized_class'],
                    'confidence': result['confidence'],
                    'hate_probability': result['hate_probability'],
                    'author_handle': row.get('author_handle', ''),
                    'like_count_visible': row.get('like_count_visible', ''),
                    'timestamp_visible': row.get('timestamp_visible', ''),
                    'video_id': row.get('video_id', ''),
                    'source_file': row.get('source_file', '')
                })
                
            except Exception as e:
                print(f"⚠️  Erro ao processar comentário {idx+1}: {str(e)}")
                # Adicionar resultado de erro
                results.append({
                    'id': row.get('id', idx + 1),
                    'text': text,
                    'text_length': len(text),
                    'text_features': f"Length: {len(text)}, Words: {len(text.split())}, Has_emoji: {'emoji' in text.lower()}",
                    'predicted_label': 'ERRO',
                    'method': 'error',
                    'specialized_class': 'N/A',
                    'confidence': 0.0,
                    'hate_probability': 0.0,
                    'author_handle': row.get('author_handle', ''),
                    'like_count_visible': row.get('like_count_visible', ''),
                    'timestamp_visible': row.get('timestamp_visible', ''),
                    'video_id': row.get('video_id', ''),
                    'source_file': row.get('source_file', '')
                })
        
        # Criar DataFrame com resultados
        results_df = pd.DataFrame(results)
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"out/ANALISE_TIKTOK_SPACE_{timestamp}.csv"
        results_df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"💾 Resultados salvos: {output_file}")
        
        # Estatísticas
        total_comments = len(results_df)
        hate_comments = len(results_df[results_df['predicted_label'] == 'HATE'])
        nao_hate_comments = len(results_df[results_df['predicted_label'] == 'NÃO-HATE'])
        error_comments = len(results_df[results_df['predicted_label'] == 'ERRO'])
        
        print(f"\n📈 Estatísticas da análise:")
        print(f"   - Total de comentários: {total_comments:,}")
        print(f"   - Comentários HATE: {hate_comments:,} ({hate_comments/total_comments*100:.1f}%)")
        print(f"   - Comentários NÃO-HATE: {nao_hate_comments:,} ({nao_hate_comments/total_comments*100:.1f}%)")
        print(f"   - Comentários com ERRO: {error_comments:,} ({error_comments/total_comments*100:.1f}%)")
        
        # Distribuição por método
        print(f"\n🔧 Distribuição por método:")
        method_counts = results_df['method'].value_counts()
        for method, count in method_counts.head(10).items():
            print(f"   - {method}: {count:,} ({count/total_comments*100:.1f}%)")
        
        # Distribuição por classe especializada (apenas HATE)
        hate_df = results_df[results_df['predicted_label'] == 'HATE']
        if len(hate_df) > 0:
            print(f"\n🎯 Distribuição por classe especializada (HATE):")
            class_counts = hate_df['specialized_class'].value_counts()
            for class_name, count in class_counts.items():
                print(f"   - {class_name}: {count:,} ({count/len(hate_df)*100:.1f}%)")
        
        # Amostra de casos HATE
        print(f"\n🚨 Amostra de casos HATE:")
        hate_samples = hate_df.head(5)
        for idx, row in hate_samples.iterrows():
            text_preview = row['text'][:100] + "..." if len(row['text']) > 100 else row['text']
            print(f"   - {text_preview} [{row['method']}]")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Erro ao analisar dataset do TikTok: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 Iniciando análise do dataset do TikTok...")
    output_file = analyze_tiktok_dataset()
    if output_file:
        print(f"✅ Análise concluída! Arquivo: {output_file}")
    else:
        print("❌ Falha na análise do dataset do TikTok")
