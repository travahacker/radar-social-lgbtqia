#!/usr/bin/env python3
"""
Análise Completa com Comparação de True Hate
Baseado no sistema avançado do domingo com regras contextuais
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Adicionar o diretório atual ao path para importar app
sys.path.append('.')

def load_annotated_dataset():
    """Carrega o dataset com anotações manuais"""
    print("📂 Carregando dataset com anotações manuais...")
    
    # Carregar dataset anotado
    df_annotated = pd.read_csv(
        'clean-annotated-data/Scrapping_insta_annotated_GLOBAL_REVISADO.csv',
        sep=';',
        encoding='utf-8'
    )
    
    print(f"✅ Dataset anotado carregado: {len(df_annotated)} exemplos")
    return df_annotated

def convert_annotations_to_binary(df_annotated):
    """Converte anotações para formato binário"""
    print("🔄 Convertendo anotações para formato binário...")
    
    # Mapear avaliação para is_hate
    def map_avaliacao_to_hate(avaliacao):
        if avaliacao == 'odio':
            return True
        elif avaliacao in ['positivo', 'neutro']:
            return False
        else:
            return False  # Default para casos não mapeados
    
    # Aplicar conversão
    df_annotated['true_hate'] = df_annotated['avaliacao'].apply(map_avaliacao_to_hate)
    
    # Criar dataset final
    df_final = df_annotated[['id', 'Comment Text', 'true_hate']].copy()
    df_final.columns = ['id', 'text', 'true_hate']
    
    # Remover linhas com texto vazio ou NaN
    df_final = df_final.dropna(subset=['text'])
    df_final = df_final[df_final['text'].str.strip() != '']
    
    print(f"✅ Dataset final preparado: {len(df_final)} exemplos")
    print(f"📊 Distribuição true hate: {df_final['true_hate'].value_counts().to_dict()}")
    
    return df_final

def analyze_with_space_system(df_final):
    """Analisa o dataset com o sistema do Space"""
    print("🤖 Analisando com sistema do Space...")
    
    try:
        # Importar sistema atual do Space
        from app_space_version import predict_hate_speech
        
        results = []
        correct_predictions = 0
        total_predictions = 0
        
        # Contadores para matriz de confusão
        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0
        
        # Contadores por método
        method_counts = {}
        
        # Contadores por classe especializada
        specialized_counts = {}
        
        for idx, row in df_final.iterrows():
            text = row['text']
            true_hate = row['true_hate']
            
            try:
                # Predição do sistema
                prediction = predict_hate_speech(text)
                predicted_hate = prediction['is_hate']
                
                # Análise de características do texto
                text_length = len(text)
                has_emoji = any(ord(char) > 127 for char in text)
                has_punctuation = any(p in text for p in ['!', '?', '.', ',', ';', ':'])
                has_caps = any(c.isupper() for c in text)
                
                # Verificar se está correto
                is_correct = (true_hate == predicted_hate)
                if is_correct:
                    correct_predictions += 1
                
                total_predictions += 1
                
                # Atualizar matriz de confusão
                if true_hate and predicted_hate:
                    true_positives += 1
                elif not true_hate and not predicted_hate:
                    true_negatives += 1
                elif true_hate and not predicted_hate:
                    false_negatives += 1
                elif not true_hate and predicted_hate:
                    false_positives += 1
                
                # Contar métodos
                method = prediction.get('method', 'unknown')
                method_counts[method] = method_counts.get(method, 0) + 1
                
                # Contar classes especializadas
                if predicted_hate:
                    specialized_class = prediction.get('specialized_class', 'N/A')
                    specialized_counts[specialized_class] = specialized_counts.get(specialized_class, 0) + 1
                
                results.append({
                    'id': row['id'],
                    'text': text,
                    'text_length': text_length,
                    'has_emoji': has_emoji,
                    'has_punctuation': has_punctuation,
                    'has_caps': has_caps,
                    'true_label': 'HATE' if true_hate else 'NÃO-HATE',
                    'predicted_label': 'HATE' if predicted_hate else 'NÃO-HATE',
                    'is_correct': is_correct,
                    'method': method,
                    'specialized_class': prediction.get('specialized_class', 'N/A'),
                    'confidence': prediction.get('confidence', 0.0),
                    'hate_probability': prediction.get('hate_probability', 0.0)
                })
                
                if idx % 100 == 0:
                    print(f"📊 Processados: {idx}/{len(df_final)} ({idx/len(df_final)*100:.1f}%)")
                    
            except Exception as e:
                print(f"⚠️ Erro ao processar linha {idx}: {e}")
                continue
        
        # Calcular métricas
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"✅ Análise concluída: {total_predictions} exemplos processados")
        print(f"🎯 Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
        print(f"📊 Precision: {precision:.3f}")
        print(f"📈 Recall: {recall:.3f}")
        print(f"🎯 F1-Score: {f1_score:.3f}")
        
        return results, {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'true_negatives': true_negatives,
            'false_negatives': false_negatives,
            'method_counts': method_counts,
            'specialized_counts': specialized_counts
        }
        
    except ImportError as e:
        print(f"❌ Erro ao importar sistema: {e}")
        return [], {}

def generate_comprehensive_reports(results, metrics):
    """Gera relatórios abrangentes"""
    print("📊 Gerando relatórios abrangentes...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Converter para DataFrame
    df_results = pd.DataFrame(results)
    
    if len(df_results) == 0:
        print("❌ Nenhum resultado para gerar relatórios")
        return
    
    # 1. Análise completa com true hate
    analysis_file = f"out/analise_completa_true_hate_{timestamp}.csv"
    df_results.to_csv(analysis_file, index=False, encoding='utf-8')
    print(f"📄 Análise completa: {analysis_file}")
    
    # 2. TRUE HATE (casos corretos de ódio)
    true_hate_df = df_results[(df_results['true_label'] == 'HATE') & (df_results['predicted_label'] == 'HATE')]
    true_hate_file = f"out/true_hate_corretos_{timestamp}.csv"
    true_hate_df.to_csv(true_hate_file, index=False, encoding='utf-8')
    print(f"📄 TRUE HATE corretos: {true_hate_file} ({len(true_hate_df)} casos)")
    
    # 3. FALSE POSITIVES (casos não-ódio classificados como ódio)
    false_positives_df = df_results[(df_results['true_label'] == 'NÃO-HATE') & (df_results['predicted_label'] == 'HATE')]
    false_positives_file = f"out/false_positives_{timestamp}.csv"
    false_positives_df.to_csv(false_positives_file, index=False, encoding='utf-8')
    print(f"📄 FALSE POSITIVES: {false_positives_file} ({len(false_positives_df)} casos)")
    
    # 4. FALSE NEGATIVES (casos de ódio classificados como não-ódio)
    false_negatives_df = df_results[(df_results['true_label'] == 'HATE') & (df_results['predicted_label'] == 'NÃO-HATE')]
    false_negatives_file = f"out/false_negatives_{timestamp}.csv"
    false_negatives_df.to_csv(false_negatives_file, index=False, encoding='utf-8')
    print(f"📄 FALSE NEGATIVES: {false_negatives_file} ({len(false_negatives_df)} casos)")
    
    # 5. TRUE NEGATIVES (casos corretos de não-ódio)
    true_negatives_df = df_results[(df_results['true_label'] == 'NÃO-HATE') & (df_results['predicted_label'] == 'NÃO-HATE')]
    true_negatives_file = f"out/true_negatives_{timestamp}.csv"
    true_negatives_df.to_csv(true_negatives_file, index=False, encoding='utf-8')
    print(f"📄 TRUE NEGATIVES: {true_negatives_file} ({len(true_negatives_df)} casos)")
    
    # 6. Resumo das métricas
    summary_data = {
        'metric': [
            'Total de exemplos', 'Accuracy', 'Precision', 'Recall', 'F1-Score',
            'True Positives', 'False Positives', 'True Negatives', 'False Negatives'
        ],
        'value': [
            len(df_results),
            f"{metrics.get('accuracy', 0):.3f}",
            f"{metrics.get('precision', 0):.3f}",
            f"{metrics.get('recall', 0):.3f}",
            f"{metrics.get('f1_score', 0):.3f}",
            metrics.get('true_positives', 0),
            metrics.get('false_positives', 0),
            metrics.get('true_negatives', 0),
            metrics.get('false_negatives', 0)
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    summary_file = f"out/resumo_metricas_{timestamp}.csv"
    summary_df.to_csv(summary_file, index=False, encoding='utf-8')
    print(f"📄 Resumo das métricas: {summary_file}")
    
    # 7. Análise por método
    method_analysis = df_results.groupby('method').agg({
        'is_correct': ['count', 'sum', 'mean'],
        'confidence': 'mean',
        'hate_probability': 'mean'
    }).round(3)
    
    method_analysis.columns = ['total', 'correct', 'accuracy', 'avg_confidence', 'avg_hate_prob']
    method_analysis = method_analysis.reset_index()
    
    method_file = f"out/analise_por_metodo_{timestamp}.csv"
    method_analysis.to_csv(method_file, index=False, encoding='utf-8')
    print(f"📄 Análise por método: {method_file}")
    
    # 8. Análise por classe especializada
    specialized_analysis = df_results[df_results['specialized_class'] != 'N/A'].groupby('specialized_class').agg({
        'is_correct': ['count', 'sum', 'mean'],
        'confidence': 'mean',
        'hate_probability': 'mean'
    }).round(3)
    
    specialized_analysis.columns = ['total', 'correct', 'accuracy', 'avg_confidence', 'avg_hate_prob']
    specialized_analysis = specialized_analysis.reset_index()
    
    specialized_file = f"out/analise_por_classe_{timestamp}.csv"
    specialized_analysis.to_csv(specialized_file, index=False, encoding='utf-8')
    print(f"📄 Análise por classe: {specialized_file}")
    
    return {
        'analysis_file': analysis_file,
        'true_hate_file': true_hate_file,
        'false_positives_file': false_positives_file,
        'false_negatives_file': false_negatives_file,
        'true_negatives_file': true_negatives_file,
        'summary_file': summary_file,
        'method_file': method_file,
        'specialized_file': specialized_file
    }

def main():
    """Função principal"""
    print("🚀 ANÁLISE COMPLETA COM TRUE HATE COMPARISON")
    print("=" * 60)
    
    try:
        # 1. Carregar dataset anotado
        df_annotated = load_annotated_dataset()
        
        # 2. Converter anotações para binário
        df_final = convert_annotations_to_binary(df_annotated)
        
        # 3. Analisar com sistema do Space
        results, metrics = analyze_with_space_system(df_final)
        
        # 4. Gerar relatórios abrangentes
        if results:
            files = generate_comprehensive_reports(results, metrics)
            
            print("\n" + "=" * 60)
            print("✅ ANÁLISE COMPLETA COM TRUE HATE CONCLUÍDA")
            print("=" * 60)
            print(f"📊 Accuracy: {metrics.get('accuracy', 0):.3f} ({metrics.get('accuracy', 0)*100:.1f}%)")
            print(f"📊 Precision: {metrics.get('precision', 0):.3f}")
            print(f"📈 Recall: {metrics.get('recall', 0):.3f}")
            print(f"🎯 F1-Score: {metrics.get('f1_score', 0):.3f}")
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
