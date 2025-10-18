#!/usr/bin/env python3
"""
Comparação Detalhada: Space vs Redundância
Gera planilha com análise lado a lado de ambos os sistemas
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import re

# Adicionar o diretório atual ao path
sys.path.append('.')

# Importar as funções do sistema
from app_space_version import predict_hate_speech

def analyze_context(text):
    """Analisa o contexto do texto"""
    text_lower = text.lower()
    
    # Contexto positivo
    positive_patterns = [
        r'\b(amo|adoro|gosto|aprecio|respeito|apoio|defendo)\b',
        r'\b(orgulho|pride|diversidade|inclusão|igualdade)\b',
        r'\b(❤️|💖|💕|🌈|👏|👍|🎉|✨)\b'
    ]
    
    # Contexto negativo
    negative_patterns = [
        r'\b(odeio|detesto|nojento|repugnante|asqueroso)\b',
        r'\b(🤮|🤢|😡|😠|👎|💀|👻)\b'
    ]
    
    # Contexto neutro
    neutral_patterns = [
        r'\b(acho|penso|creio|considero|opinião)\b',
        r'\b(🤔|😐|😑|😶)\b'
    ]
    
    positive_count = sum(1 for pattern in positive_patterns if re.search(pattern, text_lower))
    negative_count = sum(1 for pattern in negative_patterns if re.search(pattern, text_lower))
    neutral_count = sum(1 for pattern in neutral_patterns if re.search(pattern, text_lower))
    
    if positive_count > negative_count and positive_count > neutral_count:
        return "positivo"
    elif negative_count > positive_count and negative_count > neutral_count:
        return "negativo"
    elif neutral_count > 0:
        return "neutro"
    else:
        return "indefinido"

def analyze_linguistic_features(text):
    """Analisa características linguísticas do texto"""
    features = []
    
    # Padrões de agressividade
    if re.search(r'[A-Z]{3,}', text):
        features.append("caps_excessive")
    
    if re.search(r'[!]{2,}|[?]{2,}', text):
        features.append("punctuation_excessive")
    
    if re.search(r'\b(viado|bicha|sapatão|paneleiro|gay|lésbica|bissexual|queer)\b', text.lower()):
        features.append("lgbtqia_terms")
    
    if re.search(r'\b(trans|travesti|transgênero|transgenero)\b', text.lower()):
        features.append("trans_terms")
    
    if re.search(r'\b(doença|doente|tratamento|cura|psicológico|mental)\b', text.lower()):
        features.append("medical_context")
    
    if re.search(r'\b(pecado|deus|demônio|igreja|bíblia|cristão)\b', text.lower()):
        features.append("religious_context")
    
    if re.search(r'\b(natural|normal|anormal|aberração|erro)\b', text.lower()):
        features.append("normality_context")
    
    return ";".join(features) if features else "nenhuma"

def apply_validation_logic(prediction_result, text):
    """Aplica lógica de validação adicional para true_label"""
    
    # Extrair informações da predição
    predicted_hate = prediction_result['is_hate']
    hate_probability = prediction_result['hate_probability']
    method = prediction_result.get('method', 'model_prediction')
    confidence = prediction_result.get('confidence', 0.0)
    
    # Análise contextual
    context = analyze_context(text)
    linguistic_features = analyze_linguistic_features(text)
    
    # Lógica de conferência extra
    true_hate = predicted_hate  # Base inicial
    original_hate = predicted_hate  # Para debug
    
    # 1. Conferência por contexto (MAIS AGRESSIVA)
    if context == "positivo" and predicted_hate:
        # Se contexto é positivo mas foi classificado como hate, SEMPRE revisar
        if "lgbtqia_terms" in linguistic_features and "orgulho" in text.lower():
            # Casos de orgulho LGBTQIA+ = SEMPRE NÃO-HATE
            true_hate = False
        elif hate_probability < 0.9:  # Baixa confiança
            true_hate = False
        elif "lgbtqia_terms" in linguistic_features:
            # Manter hate se tem termos LGBTQIA+ mas sem contexto de orgulho
            true_hate = True
    
    # 2. Conferência por características linguísticas
    if "medical_context" in linguistic_features and predicted_hate:
        # Contexto médico + hate = provavelmente transfobia
        true_hate = True
    
    if "religious_context" in linguistic_features and predicted_hate:
        # Contexto religioso + hate = provavelmente transfobia
        true_hate = True
    
    if "normality_context" in linguistic_features and predicted_hate:
        # Contexto de normalidade + hate = provavelmente transfobia
        true_hate = True
    
    # 3. Conferência por padrões de falsos positivos óbvios
    if predicted_hate and context == "positivo":
        # Padrões de orgulho e afirmação = SEMPRE NÃO-HATE
        pride_patterns = [
            "com muito orgulho", "com orgulho", "sou orgulhoso", "sou orgulhosa",
            "me orgulho", "orgulho de ser", "orgulho de mim", "orgulho da minha"
        ]
        if any(pattern in text.lower() for pattern in pride_patterns):
            true_hate = False
    
    # 4. Conferência por padrões de respeito e aceitação
    if predicted_hate and context == "positivo":
        # Padrões de respeito = SEMPRE NÃO-HATE
        respect_patterns = [
            "respeitar", "respeito", "aceitar", "aceitação", "tolerância",
            "diversidade", "inclusão", "igualdade", "direitos", "direito de ser"
        ]
        if any(pattern in text.lower() for pattern in respect_patterns):
            true_hate = False
    
    # 5. Conferência por método
    if method in ['mocking_emoji_rule', 'curse_words_rule', 'direct_insults_rule']:
        # Regras específicas têm alta confiança
        true_hate = predicted_hate
    
    # 6. Conferência por threshold adaptativo
    if method == 'model_prediction':
        # Para predições do modelo, aplicar threshold mais rigoroso
        if hate_probability >= 0.7:  # Threshold mais alto para confirmação
            true_hate = True
        elif hate_probability <= 0.3:  # Threshold mais baixo para rejeição
            true_hate = False
        else:
            # Zona de incerteza - manter predição original
            true_hate = predicted_hate
    
    return true_hate, context, linguistic_features

def compare_space_vs_redundancy(df_final):
    """Compara Space vs Redundância para cada caso"""
    print("🔍 COMPARANDO SPACE VS REDUNDÂNCIA")
    print("=" * 50)
    
    results = []
    total_examples = len(df_final)
    
    for idx, row in df_final.iterrows():
        if idx % 100 == 0:
            print(f"📈 Progresso: {idx}/{total_examples} ({idx/total_examples*100:.1f}%)")
        
        text = str(row['Comment Text'])
        text_length = len(text)
        has_emoji = bool(re.search(r'[😀-🙏🌀-🗿]', text))
        has_punctuation = bool(re.search(r'[!?.,;:]', text))
        has_caps = bool(re.search(r'[A-Z]', text))
        
        # === ANÁLISE DO SPACE ===
        space_prediction = predict_hate_speech(text)
        
        space_hate = space_prediction['is_hate']
        space_label = "HATE" if space_hate else "NÃO-HATE"
        space_method = space_prediction.get('method', 'model_prediction')
        space_specialized = space_prediction.get('specialized_class', 'N/A')
        space_confidence = space_prediction.get('confidence', 0.0)
        space_hate_prob = space_prediction.get('hate_probability', 0.0)
        space_threshold = 0.05 if space_method == 'model_prediction' else 0.9
        
        # === ANÁLISE DA REDUNDÂNCIA ===
        redundancy_hate, context_analysis, linguistic_features = apply_validation_logic(space_prediction, text)
        redundancy_label = "HATE" if redundancy_hate else "NÃO-HATE"
        redundancy_threshold = 0.7 if space_method == 'model_prediction' else 0.9
        
        # === COMPARAÇÃO ===
        labels_differ = space_label != redundancy_label
        is_correct = space_hate == redundancy_hate
        
        # === DETECÇÃO DE PADRÕES ===
        pride_patterns = [
            "com muito orgulho", "com orgulho", "sou orgulhoso", "sou orgulhosa",
            "me orgulho", "orgulho de ser", "orgulho de mim", "orgulho da minha"
        ]
        has_pride_pattern = any(pattern in text.lower() for pattern in pride_patterns)
        
        respect_patterns = [
            "respeitar", "respeito", "aceitar", "aceitação", "tolerância",
            "diversidade", "inclusão", "igualdade", "direitos", "direito de ser"
        ]
        has_respect_pattern = any(pattern in text.lower() for pattern in respect_patterns)
        
        # === CLASSIFICAÇÃO DO TIPO DE CASO ===
        case_type = "normal"
        if labels_differ:
            if space_hate and not redundancy_hate:
                case_type = "falso_positivo_corrigido"
            elif not space_hate and redundancy_hate:
                case_type = "falso_negativo_corrigido"
        
        if space_hate and space_hate_prob < 0.3:
            case_type = "suspeito_space"
        
        if has_pride_pattern and space_hate:
            case_type = "orgulho_classificado_hate"
        
        if has_respect_pattern and space_hate:
            case_type = "respeito_classificado_hate"
        
        results.append({
            # === INFORMAÇÕES BÁSICAS ===
            'id': row['id'],
            'text': text,
            'text_length': text_length,
            'has_emoji': has_emoji,
            'has_punctuation': has_punctuation,
            'has_caps': has_caps,
            
            # === ANÁLISE DO SPACE ===
            'space_label': space_label,
            'space_hate': space_hate,
            'space_method': space_method,
            'space_specialized_class': space_specialized,
            'space_confidence': space_confidence,
            'space_hate_probability': space_hate_prob,
            'space_threshold_used': space_threshold,
            
            # === ANÁLISE DA REDUNDÂNCIA ===
            'redundancy_label': redundancy_label,
            'redundancy_hate': redundancy_hate,
            'redundancy_threshold_used': redundancy_threshold,
            'redundancy_context_analysis': context_analysis,
            'redundancy_linguistic_features': linguistic_features,
            
            # === COMPARAÇÃO ===
            'labels_differ': labels_differ,
            'is_correct': is_correct,
            'case_type': case_type,
            
            # === DETECÇÃO DE PADRÕES ===
            'has_pride_pattern': has_pride_pattern,
            'has_respect_pattern': has_respect_pattern,
            'context_analysis': context_analysis,
            'linguistic_features': linguistic_features,
            
            # === ANÁLISE DETALHADA ===
            'space_vs_redundancy': f"{space_label} → {redundancy_label}",
            'threshold_difference': redundancy_threshold - space_threshold,
            'confidence_level': "alta" if space_confidence >= 0.9 else "média" if space_confidence >= 0.7 else "baixa",
            'method_type': "regra_contextual" if space_method != 'model_prediction' else "modelo_binario"
        })
    
    print(f"✅ Comparação concluída: {len(results)} exemplos")
    return results

def generate_comparison_reports(results_df):
    """Gera relatórios de comparação"""
    print("📊 GERANDO RELATÓRIOS DE COMPARAÇÃO")
    print("=" * 50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Relatório principal de comparação
    main_file = f"out/comparacao_space_vs_redundancy_{timestamp}.csv"
    results_df.to_csv(main_file, index=False)
    print(f"✅ Relatório principal: {main_file}")
    
    # 2. Casos onde há diferença
    different_cases = results_df[results_df['labels_differ'] == True]
    different_file = f"out/casos_diferentes_space_vs_redundancy_{timestamp}.csv"
    different_cases.to_csv(different_file, index=False)
    print(f"✅ Casos diferentes: {different_file} ({len(different_cases)} casos)")
    
    # 3. Análise por tipo de caso
    case_type_analysis = results_df.groupby('case_type').agg({
        'id': 'count',
        'space_confidence': 'mean',
        'space_hate_probability': 'mean',
        'labels_differ': 'sum'
    }).round(3)
    case_type_file = f"out/analise_por_tipo_caso_{timestamp}.csv"
    case_type_analysis.to_csv(case_type_file)
    print(f"✅ Análise por tipo: {case_type_file}")
    
    # 4. Análise por método do Space
    method_analysis = results_df.groupby('space_method').agg({
        'id': 'count',
        'labels_differ': 'sum',
        'space_confidence': 'mean',
        'space_hate_probability': 'mean'
    }).round(3)
    method_file = f"out/analise_por_metodo_space_{timestamp}.csv"
    method_analysis.to_csv(method_file)
    print(f"✅ Análise por método: {method_file}")
    
    # 5. Casos suspeitos do Space
    suspicious_cases = results_df[results_df['case_type'] == 'suspeito_space']
    suspicious_file = f"out/casos_suspeitos_space_{timestamp}.csv"
    suspicious_cases.to_csv(suspicious_file, index=False)
    print(f"✅ Casos suspeitos: {suspicious_file} ({len(suspicious_cases)} casos)")
    
    # 6. Casos de orgulho classificados como hate
    pride_hate_cases = results_df[results_df['case_type'] == 'orgulho_classificado_hate']
    pride_hate_file = f"out/orgulho_classificado_hate_{timestamp}.csv"
    pride_hate_cases.to_csv(pride_hate_file, index=False)
    print(f"✅ Orgulho como hate: {pride_hate_file} ({len(pride_hate_cases)} casos)")
    
    # 7. Casos de respeito classificados como hate
    respect_hate_cases = results_df[results_df['case_type'] == 'respeito_classificado_hate']
    respect_hate_file = f"out/respeito_classificado_hate_{timestamp}.csv"
    respect_hate_cases.to_csv(respect_hate_file, index=False)
    print(f"✅ Respeito como hate: {respect_hate_file} ({len(respect_hate_cases)} casos)")
    
    return {
        'main_file': main_file,
        'different_file': different_file,
        'case_type_file': case_type_file,
        'method_file': method_file,
        'suspicious_file': suspicious_file,
        'pride_hate_file': pride_hate_file,
        'respect_hate_file': respect_hate_file
    }

def main():
    """Função principal"""
    print("🚀 COMPARAÇÃO DETALHADA: SPACE VS REDUNDÂNCIA")
    print("=" * 60)
    
    # Carregar dataset
    print("📂 Carregando dataset...")
    df_original = pd.read_csv(
        'clean-annotated-data/export_1757023553205_limpa.csv',
        sep=';',
        encoding='utf-8'
    )
    
    print(f"📊 Dataset carregado: {len(df_original)} exemplos")
    
    # Processar comparação
    results = compare_space_vs_redundancy(df_original)
    
    # Converter para DataFrame
    results_df = pd.DataFrame(results)
    
    # Gerar relatórios
    report_files = generate_comparison_reports(results_df)
    
    # Estatísticas finais
    print("\n📊 ESTATÍSTICAS FINAIS DA COMPARAÇÃO:")
    print("=" * 50)
    
    total_examples = len(results_df)
    different_cases = len(results_df[results_df['labels_differ'] == True])
    space_hate = len(results_df[results_df['space_label'] == 'HATE'])
    redundancy_hate = len(results_df[results_df['redundancy_label'] == 'HATE'])
    
    print(f"Total de exemplos: {total_examples}")
    print(f"Casos onde há diferença: {different_cases} ({different_cases/total_examples*100:.1f}%)")
    print(f"Space - Casos HATE: {space_hate} ({space_hate/total_examples*100:.1f}%)")
    print(f"Redundância - Casos HATE: {redundancy_hate} ({redundancy_hate/total_examples*100:.1f}%)")
    
    # Análise por tipo de caso
    case_type_dist = results_df['case_type'].value_counts()
    print(f"\nDistribuição por tipo de caso:")
    for case_type, count in case_type_dist.items():
        print(f"  • {case_type}: {count} ({count/total_examples*100:.1f}%)")
    
    # Análise por método
    method_dist = results_df['space_method'].value_counts()
    print(f"\nDistribuição por método do Space:")
    for method, count in method_dist.items():
        print(f"  • {method}: {count} ({count/total_examples*100:.1f}%)")
    
    print(f"\n✅ Comparação concluída!")
    print(f"📁 Arquivos gerados em: out/")
    
    return results_df, report_files

if __name__ == "__main__":
    results_df, report_files = main()
