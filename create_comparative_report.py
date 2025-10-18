#!/usr/bin/env python3
"""
Script para criar relatório comparativo entre Instagram, TikTok e YouTube
"""

import pandas as pd
import os
from datetime import datetime

def create_comparative_report():
    """Cria relatório comparativo entre as três redes sociais"""
    
    print("📊 Criando relatório comparativo entre redes sociais...")
    
    # Encontrar arquivos de análise mais recentes
    files = {
        'instagram': None,
        'tiktok': None,
        'youtube': None
    }
    
    # Buscar arquivo do Instagram (base limpa)
    instagram_files = [f for f in os.listdir('.') if f.startswith('export_1757023553205_limpa')]
    if instagram_files:
        files['instagram'] = instagram_files[0]
    
    # Buscar arquivo do TikTok
    tiktok_files = [f for f in os.listdir('out') if f.startswith('ANALISE_TIKTOK_SPACE_')]
    if tiktok_files:
        files['tiktok'] = sorted(tiktok_files)[-1]
    
    # Buscar arquivo do YouTube
    youtube_files = [f for f in os.listdir('out') if f.startswith('ANALISE_YOUTUBE_SPACE_')]
    if youtube_files:
        files['youtube'] = sorted(youtube_files)[-1]
    
    print(f"📱 Arquivos encontrados:")
    for platform, file in files.items():
        if file:
            print(f"   - {platform.upper()}: {file}")
        else:
            print(f"   - {platform.upper()}: ❌ Não encontrado")
    
    # Carregar dados
    data = {}
    
    # Instagram (usar análise anterior se disponível)
    instagram_analysis_files = [f for f in os.listdir('.') if f.startswith('ANALISE_COMPLETA_BASE_LIMPA_')]
    if instagram_analysis_files:
        instagram_file = sorted(instagram_analysis_files)[-1]
        try:
            df_insta = pd.read_csv(instagram_file)
            data['instagram'] = df_insta
            print(f"✅ Instagram: {len(df_insta):,} comentários carregados")
        except:
            print("⚠️  Erro ao carregar dados do Instagram")
    
    # TikTok
    if files['tiktok']:
        try:
            df_tiktok = pd.read_csv(f"out/{files['tiktok']}")
            data['tiktok'] = df_tiktok
            print(f"✅ TikTok: {len(df_tiktok):,} comentários carregados")
        except:
            print("⚠️  Erro ao carregar dados do TikTok")
    
    # YouTube
    if files['youtube']:
        try:
            df_youtube = pd.read_csv(f"out/{files['youtube']}")
            data['youtube'] = df_youtube
            print(f"✅ YouTube: {len(df_youtube):,} comentários carregados")
        except:
            print("⚠️  Erro ao carregar dados do YouTube")
    
    if not data:
        print("❌ Nenhum dado foi carregado com sucesso!")
        return
    
    # Criar relatório comparativo
    report = []
    
    print("\n📈 Gerando estatísticas comparativas...")
    
    for platform, df in data.items():
        total = len(df)
        
        # Contar HATE vs NÃO-HATE
        if 'predicted_label' in df.columns:
            hate_count = len(df[df['predicted_label'] == 'HATE'])
            nao_hate_count = len(df[df['predicted_label'] == 'NÃO-HATE'])
            hate_percentage = (hate_count / total) * 100
            nao_hate_percentage = (nao_hate_count / total) * 100
        else:
            hate_count = nao_hate_count = hate_percentage = nao_hate_percentage = 0
        
        # Distribuição por método
        method_dist = {}
        if 'method' in df.columns:
            method_counts = df['method'].value_counts()
            for method, count in method_counts.head(5).items():
                method_dist[method] = f"{count:,} ({count/total*100:.1f}%)"
        
        # Distribuição por classe especializada (HATE)
        class_dist = {}
        if 'specialized_class' in df.columns:
            hate_df = df[df['predicted_label'] == 'HATE'] if 'predicted_label' in df.columns else df
            if len(hate_df) > 0:
                class_counts = hate_df['specialized_class'].value_counts()
                for class_name, count in class_counts.items():
                    if class_name != 'N/A':
                        class_dist[class_name] = f"{count:,} ({count/len(hate_df)*100:.1f}%)"
        
        # Estatísticas de texto
        if 'text' in df.columns:
            avg_length = df['text'].str.len().mean()
            max_length = df['text'].str.len().max()
            min_length = df['text'].str.len().min()
        else:
            avg_length = max_length = min_length = 0
        
        report.append({
            'platform': platform.upper(),
            'total_comments': f"{total:,}",
            'hate_comments': f"{hate_count:,} ({hate_percentage:.1f}%)",
            'nao_hate_comments': f"{nao_hate_count:,} ({nao_hate_percentage:.1f}%)",
            'avg_text_length': f"{avg_length:.1f}",
            'max_text_length': f"{max_length}",
            'min_text_length': f"{min_length}",
            'top_methods': method_dist,
            'hate_classes': class_dist
        })
    
    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"out/RELATORIO_COMPARATIVO_REDES_SOCIAIS_{timestamp}.csv"
    
    # Criar DataFrame do relatório
    report_df = pd.DataFrame(report)
    report_df.to_csv(report_file, index=False, encoding='utf-8')
    
    print(f"💾 Relatório salvo: {report_file}")
    
    # Exibir resumo
    print(f"\n📊 RESUMO COMPARATIVO - REDES SOCIAIS")
    print("=" * 60)
    
    for item in report:
        print(f"\n🔸 {item['platform']}:")
        print(f"   📝 Total de comentários: {item['total_comments']}")
        print(f"   🚨 Comentários HATE: {item['hate_comments']}")
        print(f"   ✅ Comentários NÃO-HATE: {item['nao_hate_comments']}")
        print(f"   📏 Comprimento médio do texto: {item['avg_text_length']} caracteres")
        
        if item['top_methods']:
            print(f"   🔧 Top métodos de detecção:")
            for method, stats in list(item['top_methods'].items())[:3]:
                print(f"      - {method}: {stats}")
        
        if item['hate_classes']:
            print(f"   🎯 Classes de hate detectadas:")
            for class_name, stats in item['hate_classes'].items():
                print(f"      - {class_name}: {stats}")
    
    # Estatísticas gerais
    total_all = sum([int(item['total_comments'].replace(',', '')) for item in report])
    total_hate_all = sum([int(item['hate_comments'].split(' ')[0].replace(',', '')) for item in report])
    total_nao_hate_all = sum([int(item['nao_hate_comments'].split(' ')[0].replace(',', '')) for item in report])
    
    print(f"\n🌐 ESTATÍSTICAS GERAIS:")
    print(f"   📝 Total geral de comentários: {total_all:,}")
    print(f"   🚨 Total de HATE: {total_hate_all:,} ({total_hate_all/total_all*100:.1f}%)")
    print(f"   ✅ Total de NÃO-HATE: {total_nao_hate_all:,} ({total_nao_hate_all/total_all*100:.1f}%)")
    
    return report_file

if __name__ == "__main__":
    print("🚀 Iniciando criação do relatório comparativo...")
    output_file = create_comparative_report()
    if output_file:
        print(f"✅ Relatório criado com sucesso! Arquivo: {output_file}")
    else:
        print("❌ Falha na criação do relatório")
