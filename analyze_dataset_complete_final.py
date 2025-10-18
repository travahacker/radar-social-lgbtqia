#!/usr/bin/env python3
"""
Análise final do dataset com regras melhoradas
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Adicionar o diretório atual ao path para importar app
sys.path.append('.')

def load_original_dataset():
    """Carrega o dataset original com rótulos corretos"""
    print("📂 Carregando dataset original...")
    
    # Carregar dataset original (pular primeira linha que não é cabeçalho)
    df_original = pd.read_csv(
        'clean-annotated-data/export_1757023553205_limpa.csv',
        sep=';',
        encoding='utf-8'
    )
    
    print(f"✅ Dataset original carregado: {len(df_original)} exemplos")
    return df_original

def convert_labels_correctly(df_original):
    """Converte rótulos do dataset original para formato binário correto"""
    print("🔄 Convertendo rótulos corretamente...")
    
    # Para o dataset limpo, não temos rótulos de hate, então vamos usar o sistema para gerar
    # Criar dataset final
    df_final = df_original[['id', 'Comment Text']].copy()
    df_final.columns = ['id', 'text']
    
    # Adicionar coluna is_hate como None (será preenchida pelo sistema)
    df_final['is_hate'] = None
    
    # Remover linhas com texto vazio ou NaN
    df_final = df_final.dropna(subset=['text'])
    df_final = df_final[df_final['text'].str.strip() != '']
    
    print(f"✅ Dataset final corrigido: {len(df_final)} exemplos")
    print(f"📊 Distribuição: {df_final['is_hate'].value_counts().to_dict()}")
    
    return df_final

def analyze_with_improved_system(df_final):
    """Analisa o dataset com o sistema melhorado"""
    print("🤖 Analisando com sistema melhorado...")
    
    try:
        # Importar sistema atual do Space
        from app_space_version import predict_hate_speech
        
        results = []
        correct_predictions = 0
        total_predictions = 0
        
        for idx, row in df_final.iterrows():
            text = row['text']
            
            try:
                # Predição do sistema
                prediction = predict_hate_speech(text)
                predicted_hate = prediction['is_hate']
                
                # Análise de características do texto
                text_length = len(text)
                has_emoji = any(ord(char) > 127 for char in text)  # Detecção simples de emoji
                has_punctuation = any(p in text for p in ['!', '?', '.', ',', ';', ':'])
                has_caps = any(c.isupper() for c in text)
                
                total_predictions += 1
                
                results.append({
                    'id': row['id'],
                    'text': text,
                    'text_length': text_length,
                    'has_emoji': has_emoji,
                    'has_punctuation': has_punctuation,
                    'has_caps': has_caps,
                    'predicted_label': 'HATE' if predicted_hate else 'NÃO-HATE',
                    'method': prediction.get('method', 'unknown'),
                    'specialized_class': prediction.get('specialized_class', 'N/A'),
                    'confidence': prediction.get('confidence', 0.0),
                    'hate_probability': prediction.get('hate_probability', 0.0)
                })
                
                if idx % 100 == 0:
                    print(f"📊 Processados: {idx}/{len(df_final)} ({idx/len(df_final)*100:.1f}%)")
                    
            except Exception as e:
                print(f"⚠️ Erro ao processar linha {idx}: {e}")
                continue
        
        # Contar hate vs não-hate
        hate_count = sum(1 for r in results if r['predicted_label'] == 'HATE')
        non_hate_count = total_predictions - hate_count
        
        print(f"✅ Análise concluída: {total_predictions} exemplos processados")
        print(f"📊 Distribuição: {hate_count} HATE, {non_hate_count} NÃO-HATE ({hate_count/total_predictions*100:.1f}% hate)")
        
        return results, hate_count/total_predictions
        
    except ImportError as e:
        print(f"❌ Erro ao importar sistema: {e}")
        return [], 0.0

def generate_final_reports(results, hate_percentage):
    """Gera relatórios finais em CSV"""
    print("📊 Gerando relatórios finais...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Converter para DataFrame
    df_results = pd.DataFrame(results)
    
    if len(df_results) == 0:
        print("❌ Nenhum resultado para gerar relatórios")
        return
    
    # 1. Análise completa
    analysis_file = f"out/analise_dataset_completa_{timestamp}.csv"
    df_results.to_csv(analysis_file, index=False, encoding='utf-8')
    print(f"📄 Análise completa: {analysis_file}")
    
    # 2. Casos de hate detectados
    hate_cases = df_results[df_results['predicted_label'] == 'HATE']
    hate_file = f"out/casos_hate_detectados_{timestamp}.csv"
    hate_cases.to_csv(hate_file, index=False, encoding='utf-8')
    print(f"📄 Casos de hate: {hate_file} ({len(hate_cases)} casos)")
    
    # 3. Resumo da análise
    summary_data = {
        'metric': ['Total de exemplos', 'Hate detectado', 'Não-hate', 'Percentual hate', 'Confiança média'],
        'value': [
            len(df_results),
            len(hate_cases),
            len(df_results) - len(hate_cases),
            f"{hate_percentage:.1%}",
            f"{df_results['confidence'].mean():.3f}"
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    summary_file = f"out/resumo_analise_{timestamp}.csv"
    summary_df.to_csv(summary_file, index=False, encoding='utf-8')
    print(f"📄 Resumo da análise: {summary_file}")
    
    # 4. Análise por método
    method_analysis = df_results.groupby('method').agg({
        'predicted_label': 'count',
        'confidence': 'mean',
        'hate_probability': 'mean'
    }).round(3)
    
    method_analysis.columns = ['total', 'avg_confidence', 'avg_hate_prob']
    method_analysis = method_analysis.reset_index()
    
    method_file = f"out/analise_por_metodo_{timestamp}.csv"
    method_analysis.to_csv(method_file, index=False, encoding='utf-8')
    print(f"📄 Análise por método: {method_file}")
    
    # 5. Análise por classe especializada
    specialized_analysis = df_results[df_results['specialized_class'] != 'N/A'].groupby('specialized_class').agg({
        'predicted_label': 'count',
        'confidence': 'mean',
        'hate_probability': 'mean'
    }).round(3)
    
    specialized_analysis.columns = ['total', 'avg_confidence', 'avg_hate_prob']
    specialized_analysis = specialized_analysis.reset_index()
    
    specialized_file = f"out/analise_por_classe_{timestamp}.csv"
    specialized_analysis.to_csv(specialized_file, index=False, encoding='utf-8')
    print(f"📄 Análise por classe: {specialized_file}")
    
    return {
        'analysis_file': analysis_file,
        'hate_file': hate_file,
        'summary_file': summary_file,
        'method_file': method_file,
        'specialized_file': specialized_file
    }

def main():
    """Função principal"""
    print("🚀 ANÁLISE FINAL COM REGRAS MELHORADAS")
    print("=" * 60)
    
    try:
        # 1. Carregar dataset original
        df_original = load_original_dataset()
        
        # 2. Converter rótulos corretamente
        df_final = convert_labels_correctly(df_original)
        
        # 3. Analisar com sistema melhorado
        results, hate_percentage = analyze_with_improved_system(df_final)
        
        # 4. Gerar relatórios finais
        if results:
            files = generate_final_reports(results, hate_percentage)
            
            print("\n" + "=" * 60)
            print("✅ ANÁLISE FINAL MELHORADA CONCLUÍDA")
            print("=" * 60)
            print(f"📊 Percentual de hate detectado: {hate_percentage:.1%}")
            print(f"📄 Arquivos gerados:")
            for key, file in files.items():
                print(f"  • {file}")
        else:
            print("❌ Falha na análise - nenhum resultado gerado")
            
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
