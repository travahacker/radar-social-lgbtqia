#!/usr/bin/env python3
"""
Script para analisar apenas o Instagram com as correções aplicadas
"""

import pandas as pd
import os
from datetime import datetime
from app_space_version import predict_hate_speech

def analyze_instagram_corrected():
    """Analisa o dataset do Instagram com as correções aplicadas"""
    
    file_path = 'clean-annotated-data/export_1757023553205_limpa.csv'
    
    print("📱 Analisando INSTAGRAM com correções...")
    print(f"📂 Arquivo: {file_path}")
    
    try:
        # Carregar dados com separador correto
        df = pd.read_csv(file_path, sep=';')
        print(f"📊 Total de comentários: {len(df):,}")
        
        # Verificar coluna de texto
        text_col = 'Comment Text'
        if text_col not in df.columns:
            print(f"❌ Coluna '{text_col}' não encontrada!")
            return None
        
        # Lista para armazenar resultados
        results = []
        
        print("🔍 Iniciando análise com sistema corrigido...")
        
        # Processar cada comentário
        for idx, row in df.iterrows():
            if idx % 100 == 0:
                print(f"📈 Processando comentário {idx+1:,}/{len(df):,}")
            
            text = str(row[text_col])
            
            try:
                # Usar sistema corrigido
                result = predict_hate_speech(text)
                
                # Adicionar resultado
                result_row = {
                    'platform': 'Instagram',
                    'id': row.get('id', idx + 1),
                    'text': text,
                    'text_length': len(text),
                    'text_features': f"Length: {len(text)}, Words: {len(text.split())}, Has_emoji: {'emoji' in text.lower()}",
                    'predicted_label': 'HATE' if result['is_hate'] else 'NÃO-HATE',
                    'method': result['method'],
                    'specialized_class': result['specialized_class'],
                    'confidence': result['confidence'],
                    'hate_probability': result['hate_probability'],
                    'author_handle': row.get('Author Handle', ''),
                    'like_count': row.get('Like Count', ''),
                    'timestamp': row.get('Timestamp', '')
                }
                
                results.append(result_row)
                
            except Exception as e:
                print(f"⚠️  Erro ao processar comentário {idx+1}: {str(e)}")
                # Adicionar resultado de erro
                result_row = {
                    'platform': 'Instagram',
                    'id': row.get('id', idx + 1),
                    'text': text,
                    'text_length': len(text),
                    'text_features': f"Length: {len(text)}, Words: {len(text.split())}, Has_emoji: {'emoji' in text.lower()}",
                    'predicted_label': 'ERRO',
                    'method': 'error',
                    'specialized_class': 'N/A',
                    'confidence': 0.0,
                    'hate_probability': 0.0,
                    'author_handle': row.get('Author Handle', ''),
                    'like_count': row.get('Like Count', ''),
                    'timestamp': row.get('Timestamp', '')
                }
                results.append(result_row)
        
        # Criar DataFrame com resultados
        results_df = pd.DataFrame(results)
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"out/ANALISE_INSTAGRAM_CORRIGIDO_{timestamp}.csv"
        results_df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"💾 Resultados salvos: {output_file}")
        
        # Estatísticas
        total_comments = len(results_df)
        hate_comments = len(results_df[results_df['predicted_label'] == 'HATE'])
        nao_hate_comments = len(results_df[results_df['predicted_label'] == 'NÃO-HATE'])
        error_comments = len(results_df[results_df['predicted_label'] == 'ERRO'])
        
        print(f"\n📈 Estatísticas da análise (Instagram):")
        print(f"   - Total de comentários: {total_comments:,}")
        print(f"   - Comentários HATE: {hate_comments:,} ({hate_comments/total_comments*100:.1f}%)")
        print(f"   - Comentários NÃO-HATE: {nao_hate_comments:,} ({nao_hate_comments/total_comments*100:.1f}%)")
        print(f"   - Comentários com ERRO: {error_comments:,} ({error_comments/total_comments*100:.1f}%)")
        
        # Distribuição por método
        print(f"\n🔧 Top métodos de detecção (Instagram):")
        method_counts = results_df['method'].value_counts()
        for method, count in method_counts.head(5).items():
            print(f"   - {method}: {count:,} ({count/total_comments*100:.1f}%)")
        
        # Distribuição por classe especializada (apenas HATE)
        hate_df = results_df[results_df['predicted_label'] == 'HATE']
        if len(hate_df) > 0:
            print(f"\n🎯 Distribuição por classe especializada (Instagram):")
            class_counts = hate_df['specialized_class'].value_counts()
            for class_name, count in class_counts.items():
                if class_name != 'N/A':
                    print(f"   - {class_name}: {count:,} ({count/len(hate_df)*100:.1f}%)")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Erro ao analisar Instagram: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 Iniciando análise do Instagram com correções...")
    output_file = analyze_instagram_corrected()
    if output_file:
        print(f"✅ Análise do Instagram concluída! Arquivo: {output_file}")
    else:
        print("❌ Falha na análise do Instagram")
