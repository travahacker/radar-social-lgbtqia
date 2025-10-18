#!/usr/bin/env python3
"""
Script para análise completa com correções aplicadas nos três datasets
"""

import pandas as pd
import os
from datetime import datetime
from app_space_version import predict_hate_speech

def analyze_all_datasets():
    """Analisa todos os três datasets com as correções aplicadas"""
    
    # Arquivos para análise
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
    
    print("🚀 ANÁLISE COMPLETA COM CORREÇÕES APLICADAS")
    print("=" * 60)
    
    all_results = []
    
    for platform, file_path in datasets.items():
        print(f"\n📱 Analisando {platform.upper()}...")
        print(f"📂 Arquivo: {file_path}")
        
        try:
            # Carregar dados com separador correto
            if platform == 'Instagram':
                df = pd.read_csv(file_path, sep=';')
            else:
                df = pd.read_csv(file_path)
            print(f"📊 Total de comentários: {len(df):,}")
            
            # Verificar coluna de texto
            text_col = text_columns[platform]
            if text_col not in df.columns:
                print(f"❌ Coluna '{text_col}' não encontrada!")
                continue
            
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
                        'platform': platform,
                        'id': row.get('id', idx + 1),
                        'text': text,
                        'text_length': len(text),
                        'text_features': f"Length: {len(text)}, Words: {len(text.split())}, Has_emoji: {'emoji' in text.lower()}",
                        'predicted_label': 'HATE' if result['is_hate'] else 'NÃO-HATE',
                        'method': result['method'],
                        'specialized_class': result['specialized_class'],
                        'confidence': result['confidence'],
                        'hate_probability': result['hate_probability']
                    }
                    
                    # Adicionar colunas específicas de cada plataforma
                    if platform == 'Instagram':
                        result_row.update({
                            'author_handle': row.get('Author Handle', ''),
                            'like_count': row.get('Like Count', ''),
                            'timestamp': row.get('Timestamp', '')
                        })
                    elif platform == 'TikTok':
                        result_row.update({
                            'author_handle': row.get('author_handle', ''),
                            'like_count_visible': row.get('like_count_visible', ''),
                            'timestamp_visible': row.get('timestamp_visible', ''),
                            'video_id': row.get('video_id', '')
                        })
                    elif platform == 'YouTube':
                        result_row.update({
                            'titulo_video': row.get('titulo_video', ''),
                            'data': row.get('data', ''),
                            'likes_comentario': row.get('likes_comentario', ''),
                            'autor_handle': row.get('autor_handle', '')
                        })
                    
                    results.append(result_row)
                    
                except Exception as e:
                    print(f"⚠️  Erro ao processar comentário {idx+1}: {str(e)}")
                    # Adicionar resultado de erro
                    result_row = {
                        'platform': platform,
                        'id': row.get('id', idx + 1),
                        'text': text,
                        'text_length': len(text),
                        'text_features': f"Length: {len(text)}, Words: {len(text.split())}, Has_emoji: {'emoji' in text.lower()}",
                        'predicted_label': 'ERRO',
                        'method': 'error',
                        'specialized_class': 'N/A',
                        'confidence': 0.0,
                        'hate_probability': 0.0
                    }
                    results.append(result_row)
            
            # Criar DataFrame com resultados
            results_df = pd.DataFrame(results)
            
            # Salvar resultados individuais
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"out/ANALISE_{platform.upper()}_CORRIGIDO_{timestamp}.csv"
            results_df.to_csv(output_file, index=False, encoding='utf-8')
            
            print(f"💾 Resultados salvos: {output_file}")
            
            # Estatísticas
            total_comments = len(results_df)
            hate_comments = len(results_df[results_df['predicted_label'] == 'HATE'])
            nao_hate_comments = len(results_df[results_df['predicted_label'] == 'NÃO-HATE'])
            error_comments = len(results_df[results_df['predicted_label'] == 'ERRO'])
            
            print(f"\n📈 Estatísticas da análise ({platform}):")
            print(f"   - Total de comentários: {total_comments:,}")
            print(f"   - Comentários HATE: {hate_comments:,} ({hate_comments/total_comments*100:.1f}%)")
            print(f"   - Comentários NÃO-HATE: {nao_hate_comments:,} ({nao_hate_comments/total_comments*100:.1f}%)")
            print(f"   - Comentários com ERRO: {error_comments:,} ({error_comments/total_comments*100:.1f}%)")
            
            # Distribuição por método
            print(f"\n🔧 Top métodos de detecção ({platform}):")
            method_counts = results_df['method'].value_counts()
            for method, count in method_counts.head(5).items():
                print(f"   - {method}: {count:,} ({count/total_comments*100:.1f}%)")
            
            # Distribuição por classe especializada (apenas HATE)
            hate_df = results_df[results_df['predicted_label'] == 'HATE']
            if len(hate_df) > 0:
                print(f"\n🎯 Distribuição por classe especializada ({platform}):")
                class_counts = hate_df['specialized_class'].value_counts()
                for class_name, count in class_counts.items():
                    if class_name != 'N/A':
                        print(f"   - {class_name}: {count:,} ({count/len(hate_df)*100:.1f}%)")
            
            # Adicionar à lista geral
            all_results.extend(results)
            
        except Exception as e:
            print(f"❌ Erro ao analisar {platform}: {str(e)}")
            continue
    
    # Criar relatório consolidado
    if all_results:
        print(f"\n📊 GERANDO RELATÓRIO CONSOLIDADO...")
        
        all_results_df = pd.DataFrame(all_results)
        
        # Salvar relatório consolidado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        consolidated_file = f"out/ANALISE_CONSOLIDADA_CORRIGIDA_{timestamp}.csv"
        all_results_df.to_csv(consolidated_file, index=False, encoding='utf-8')
        
        print(f"💾 Relatório consolidado salvo: {consolidated_file}")
        
        # Estatísticas gerais
        total_all = len(all_results_df)
        hate_all = len(all_results_df[all_results_df['predicted_label'] == 'HATE'])
        nao_hate_all = len(all_results_df[all_results_df['predicted_label'] == 'NÃO-HATE'])
        
        print(f"\n🌐 ESTATÍSTICAS GERAIS (TODAS AS PLATAFORMAS):")
        print(f"   - Total de comentários: {total_all:,}")
        print(f"   - Comentários HATE: {hate_all:,} ({hate_all/total_all*100:.1f}%)")
        print(f"   - Comentários NÃO-HATE: {nao_hate_all:,} ({nao_hate_all/total_all*100:.1f}%)")
        
        # Estatísticas por plataforma
        print(f"\n📱 ESTATÍSTICAS POR PLATAFORMA:")
        for platform in ['Instagram', 'TikTok', 'YouTube']:
            platform_df = all_results_df[all_results_df['platform'] == platform]
            if len(platform_df) > 0:
                platform_hate = len(platform_df[platform_df['predicted_label'] == 'HATE'])
                platform_total = len(platform_df)
                print(f"   - {platform}: {platform_hate:,}/{platform_total:,} ({platform_hate/platform_total*100:.1f}% HATE)")
        
        return consolidated_file
    
    return None

if __name__ == "__main__":
    print("🚀 Iniciando análise completa com correções...")
    output_file = analyze_all_datasets()
    if output_file:
        print(f"✅ Análise completa concluída! Arquivo: {output_file}")
    else:
        print("❌ Falha na análise completa")
