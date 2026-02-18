"""
Sistema Integrado de Análise de Vídeos
Detecta sinais de:
- Depressão (expressões faciais e fala)
- Hematomas (possível violência doméstica)
- Marcas e machucados (problemas de saúde)
"""

import os
import json
from datetime import datetime
from video_analysis import VideoAnalyzer
from audio_analysis import AudioAnalyzer


class IntegratedAnalyzer:
    """Análise integrada de vídeo e áudio"""

    def __init__(self, video_path):
        self.video_path = video_path
        self.video_analyzer = VideoAnalyzer(video_path)
        self.audio_analyzer = AudioAnalyzer(video_path)
        self.integrated_results = {}

    def analyze(self):
        """Executa análise completa"""
        print("="*80)
        print("SISTEMA INTEGRADO DE ANÁLISE DE VÍDEO")
        print("Detecção de Depressão, Violência Doméstica e Problemas de Saúde")
        print("="*80)
        print()

        # Análise de vídeo (expressões, hematomas, marcas)
        print("\n" + "="*80)
        print("ETAPA 1: ANÁLISE VISUAL (Vídeo)")
        print("="*80)
        video_results = self.video_analyzer.analyze_video(sample_rate=30)
        video_report = self.video_analyzer.generate_report(
            'analysis_report.json')

        # Análise de áudio (fala)
        print("\n" + "="*80)
        print("ETAPA 2: ANÁLISE DE ÁUDIO (Fala)")
        print("="*80)
        audio_results = self.audio_analyzer.analyze()

        if audio_results['transcricao']:
            audio_report = self.audio_analyzer.generate_report(
                'audio_analysis_report.json')
        else:
            audio_report = None

        # Integra resultados
        self._integrate_results(video_report, audio_report)

        # Gera relatório final integrado
        self.generate_final_report()

        return self.integrated_results

    def _integrate_results(self, video_report, audio_report):
        """Integra resultados de vídeo e áudio"""
        self.integrated_results = {
            'arquivo': self.video_path,
            'timestamp': datetime.now().isoformat(),

            'video_analysis': video_report,
            'audio_analysis': audio_report if audio_report else {
                'disponivel': False,
                'motivo': 'Análise de áudio não concluída'
            },

            'analise_integrada': {}
        }

        # Calcula scores integrados
        depression_score_visual = video_report['analise_depressao']['score']
        depression_score_audio = 0

        if audio_report:
            depression_score_audio = audio_report['analise_fala']['score_depressao']

        # Score total de depressão (média ponderada)
        total_depression_score = (
            depression_score_visual * 0.4 + depression_score_audio * 0.6)

        # Classificação integrada
        self.integrated_results['analise_integrada'] = {
            'depressao': {
                'score_total': round(total_depression_score, 2),
                'score_visual': depression_score_visual,
                'score_audio': depression_score_audio,
                'nivel_risco': self._classify_depression_risk(total_depression_score),
                'recomendacao_final': self._get_final_depression_recommendation(
                    total_depression_score, video_report, audio_report
                )
            },
            'violencia_domestica': {
                'hematomas_detectados': video_report['analise_hematomas']['total_detectado'],
                'score_risco': video_report['analise_hematomas']['score_risco'],
                'nivel_risco': video_report['analise_hematomas']['nivel_risco'],
                'recomendacao': video_report['analise_hematomas']['recomendacao']
            },
            'problemas_saude': {
                'marcas_detectadas': video_report['analise_marcas']['total_detectado'],
                'recomendacao': video_report['analise_marcas']['recomendacao']
            }
        }

    def _classify_depression_risk(self, score):
        """Classifica o risco de depressão"""
        if score < 3:
            return 'BAIXO'
        elif score < 8:
            return 'MODERADO'
        elif score < 15:
            return 'ALTO'
        else:
            return 'MUITO ALTO - URGENTE'

    def _get_final_depression_recommendation(self, score, video_report, audio_report):
        """Gera recomendação final para depressão"""
        recommendations = []

        if score < 3:
            recommendations.append(
                "✓ Não foram detectados sinais significativos de depressão.")
            recommendations.append(
                "✓ Continue mantendo hábitos saudáveis e rede de apoio.")

        elif score < 8:
            recommendations.append(
                "⚠ ATENÇÃO: Alguns indicadores de depressão foram detectados.")
            recommendations.append("⚠ Recomendações:")
            recommendations.append(
                "  • Converse com pessoas de confiança sobre como você se sente")
            recommendations.append("  • Considere procurar apoio psicológico")
            recommendations.append(
                "  • Mantenha rotina de sono e alimentação saudável")
            recommendations.append(
                "  • Pratique atividades físicas regularmente")

        elif score < 15:
            recommendations.append(
                "🚨 ALERTA: Múltiplos indicadores de depressão detectados.")
            recommendations.append("🚨 RECOMENDAÇÃO URGENTE:")
            recommendations.append(
                "  • Procure IMEDIATAMENTE um profissional de saúde mental")
            recommendations.append(
                "  • Um psicólogo ou psiquiatra pode fazer avaliação adequada")
            recommendations.append("  • Não enfrente isso sozinho(a)")
            recommendations.append(
                "  • CVV - Centro de Valorização da Vida: 188 (24h, gratuito)")

        else:
            recommendations.append(
                "🆘 URGÊNCIA MÁXIMA: Sinais graves de depressão detectados.")
            recommendations.append("🆘 AÇÃO IMEDIATA NECESSÁRIA:")
            recommendations.append("  • LIGUE AGORA: CVV 188 ou SAMU 192")
            recommendations.append(
                "  • Procure IMEDIATAMENTE atendimento médico de emergência")
            recommendations.append(
                "  • Informe familiares e amigos sobre sua situação")
            recommendations.append(
                "  • Você não está sozinho(a) e há ajuda disponível")

        # Adiciona contexto específico
        if video_report['analise_depressao']['indicadores_encontrados']:
            recommendations.append("\nIndicadores Visuais:")
            for ind in video_report['analise_depressao']['indicadores_encontrados'][:3]:
                recommendations.append(f"  • {ind}")

        if audio_report and audio_report['analise_fala']['palavras_chave_encontradas']:
            recommendations.append("\nIndicadores na Fala:")
            palavras = audio_report['analise_fala']['palavras_chave_encontradas'][:5]
            recommendations.append(
                f"  • Palavras-chave detectadas: {', '.join(palavras)}")

        return '\n'.join(recommendations)

    def generate_final_report(self):
        """Gera relatório final consolidado"""
        output_json = 'RELATORIO_FINAL_INTEGRADO.json'
        output_txt = 'RELATORIO_FINAL_INTEGRADO.txt'

        # Salva JSON
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(self.integrated_results, f, indent=4, ensure_ascii=False)

        # Gera relatório em texto
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("RELATÓRIO FINAL INTEGRADO - ANÁLISE DE VÍDEO\n")
            f.write(
                "Sistema de Detecção de Depressão, Violência Doméstica e Problemas de Saúde\n")
            f.write("="*80 + "\n\n")

            f.write(
                f"Arquivo Analisado: {self.integrated_results['arquivo']}\n")
            f.write(
                f"Data/Hora da Análise: {self.integrated_results['timestamp']}\n\n")

            # Resumo Executivo
            f.write("="*80 + "\n")
            f.write("RESUMO EXECUTIVO\n")
            f.write("="*80 + "\n\n")

            integrated = self.integrated_results['analise_integrada']

            # Depressão
            f.write("1. ANÁLISE DE DEPRESSÃO\n")
            f.write("-"*80 + "\n")
            f.write(f"Score Total: {integrated['depressao']['score_total']}\n")
            f.write(
                f"Nível de Risco: {integrated['depressao']['nivel_risco']}\n")
            f.write(
                f"Score Visual (Expressões): {integrated['depressao']['score_visual']}\n")
            f.write(
                f"Score Áudio (Fala): {integrated['depressao']['score_audio']}\n\n")
            f.write("RECOMENDAÇÃO:\n")
            f.write(integrated['depressao']['recomendacao_final'] + "\n\n")

            # Violência Doméstica
            f.write("2. ANÁLISE DE POSSÍVEL VIOLÊNCIA DOMÉSTICA (Hematomas)\n")
            f.write("-"*80 + "\n")
            f.write(
                f"Hematomas Detectados: {integrated['violencia_domestica']['hematomas_detectados']}\n")
            f.write(
                f"Score de Risco: {integrated['violencia_domestica']['score_risco']}\n")
            f.write(
                f"Nível de Risco: {integrated['violencia_domestica']['nivel_risco']}\n\n")
            f.write("RECOMENDAÇÃO:\n")
            f.write(integrated['violencia_domestica']['recomendacao'] + "\n\n")

            # Problemas de Saúde
            f.write("3. ANÁLISE DE PROBLEMAS DE SAÚDE (Marcas e Machucados)\n")
            f.write("-"*80 + "\n")
            f.write(
                f"Marcas Detectadas: {integrated['problemas_saude']['marcas_detectadas']}\n\n")
            f.write("RECOMENDAÇÃO:\n")
            f.write(integrated['problemas_saude']['recomendacao'] + "\n\n")

            # Informações de Suporte
            f.write("="*80 + "\n")
            f.write("RECURSOS E LINHAS DE APOIO\n")
            f.write("="*80 + "\n\n")

            f.write("SAÚDE MENTAL:\n")
            f.write("• CVV - Centro de Valorização da Vida: 188 (24h, gratuito)\n")
            f.write(
                "• CAPS - Centro de Atenção Psicossocial (busque o mais próximo)\n")
            f.write("• SAMU: 192 (emergências)\n\n")

            f.write("VIOLÊNCIA DOMÉSTICA:\n")
            f.write("• Central de Atendimento à Mulher: 180 (24h, gratuito)\n")
            f.write("• Polícia Militar: 190\n")
            f.write("• Delegacia da Mulher (busque a mais próxima)\n")
            f.write("• Disque Direitos Humanos: 100\n\n")

            f.write("SAÚDE GERAL:\n")
            f.write("• SAMU: 192\n")
            f.write("• UBS - Unidade Básica de Saúde (busque a mais próxima)\n\n")

            f.write("="*80 + "\n")
            f.write("IMPORTANTE\n")
            f.write("="*80 + "\n")
            f.write(
                "Esta análise é baseada em inteligência artificial e processamento de imagem.\n")
            f.write("NÃO substitui avaliação profissional médica ou psicológica.\n")
            f.write("Em caso de risco, procure ajuda profissional IMEDIATAMENTE.\n")
            f.write("="*80 + "\n")

        print("\n" + "="*80)
        print("RELATÓRIOS GERADOS:")
        print("="*80)
        print(f"✓ {output_json}")
        print(f"✓ {output_txt}")
        print(f"✓ analysis_report.json (detalhes visuais)")
        print(f"✓ analysis_report.txt (detalhes visuais)")
        if self.integrated_results['audio_analysis'].get('disponivel', True):
            print(f"✓ audio_analysis_report.json (detalhes áudio)")
            print(f"✓ audio_analysis_report.txt (detalhes áudio)")
        print("="*80)


def main():
    """Função principal"""
    video_path = 'data/YTDown.com_YouTube_Media_5t_FoFzVcsA_001_720p.mp4'

    if not os.path.exists(video_path):
        print(f"ERRO: Vídeo não encontrado em {video_path}")
        return

    # Cria analisador integrado
    analyzer = IntegratedAnalyzer(video_path)

    # Executa análise completa
    results = analyzer.analyze()

    print("\n" + "="*80)
    print("ANÁLISE CONCLUÍDA!")
    print("="*80)

    # Mostra resumo
    integrated = results['analise_integrada']

    print(f"\n📊 RESUMO DOS RESULTADOS:")
    print(f"\n1. DEPRESSÃO:")
    print(f"   Nível de Risco: {integrated['depressao']['nivel_risco']}")
    print(f"   Score Total: {integrated['depressao']['score_total']}")

    print(f"\n2. VIOLÊNCIA DOMÉSTICA:")
    print(
        f"   Hematomas Detectados: {integrated['violencia_domestica']['hematomas_detectados']}")
    print(
        f"   Nível de Risco: {integrated['violencia_domestica']['nivel_risco']}")

    print(f"\n3. PROBLEMAS DE SAÚDE:")
    print(
        f"   Marcas Detectadas: {integrated['problemas_saude']['marcas_detectadas']}")

    print("\n" + "="*80)
    print("Consulte os relatórios gerados para informações detalhadas.")
    print("="*80)


if __name__ == "__main__":
    main()
