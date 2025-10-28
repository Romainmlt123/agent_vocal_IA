#!/usr/bin/env python3
"""
Demo CLI for Agent Vocal IA.

Demonstrates the complete pipeline: Voice → Transcription → RAG → LLM → TTS
"""

import argparse
import sys
from pathlib import Path

from src.orchestrator import VocalTutorOrchestrator
from src.utils import format_time, get_config, setup_logging


def print_banner():
    """Print welcome banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🎓  AGENT VOCAL IA - TUTEUR ÉDUCATIF LOCAL  🎓        ║
║                                                               ║
║     Assistant vocal 100% offline pour l'apprentissage        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_section(title: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(label: str, value: str, indent: int = 2):
    """Print a result line."""
    prefix = " " * indent
    print(f"{prefix}{label}: {value}")


def demo_text_mode(orchestrator: VocalTutorOrchestrator, question: str, subject: str = None):
    """
    Run demo in text mode.
    
    Args:
        orchestrator: Orchestrator instance
        question: Text question
        subject: Optional subject
    """
    print_section("MODE TEXTE - Démonstration")
    
    print(f"\n📝 Question:")
    print(f"   {question}")
    
    if subject:
        print(f"\n📚 Matière sélectionnée: {subject}")
    else:
        print(f"\n🔍 Détection automatique de la matière...")
    
    print("\n⏳ Traitement en cours...")
    print("   [1/3] Recherche de contexte dans les documents...")
    print("   [2/3] Génération de la réponse par le LLM...")
    print("   [3/3] Synthèse vocale...")
    
    # Process
    results = orchestrator.process_text_question(question, subject=subject, generate_audio=True)
    
    # Display results
    if results.get('success'):
        print_section("✅ RÉSULTATS")
        
        print_result("Matière détectée", results.get('subject', 'N/A'))
        print_result("Temps de traitement", format_time(results.get('processing_time', 0)))
        
        # Sources
        sources = results.get('sources', [])
        if sources:
            print(f"\n📚 Sources utilisées ({len(sources)}):")
            for src in sources:
                print(f"   • {src['filename']} (score: {src['score']:.3f})")
        else:
            print("\n📚 Aucune source trouvée (réponse sans RAG)")
        
        # Response
        print(f"\n💡 Réponse du tuteur:")
        print("-" * 70)
        response = results.get('response', '')
        for line in response.split('\n'):
            print(f"  {line}")
        print("-" * 70)
        
        # Hints
        hints = results.get('hints', {})
        if any(hints.values()):
            print(f"\n🎓 Indices progressifs extraits:")
            for level, hint in hints.items():
                if hint:
                    print(f"\n  {level.replace('_', ' ').title()}:")
                    for line in hint.split('\n'):
                        if line.strip():
                            print(f"    {line}")
        
        # Audio
        audio_path = results.get('audio_output')
        if audio_path:
            print(f"\n🔊 Audio généré: {audio_path}")
            print("   Vous pouvez le lire avec: aplay, vlc, ou tout autre lecteur")
        
        print_section("✅ DÉMONSTRATION TERMINÉE")
        
    else:
        print_section("❌ ERREUR")
        print(f"\n{results.get('error', 'Erreur inconnue')}")


def demo_audio_mode(orchestrator: VocalTutorOrchestrator, audio_path: str, subject: str = None):
    """
    Run demo in audio mode.
    
    Args:
        orchestrator: Orchestrator instance
        audio_path: Path to audio file
        subject: Optional subject
    """
    print_section("MODE VOCAL - Démonstration")
    
    print(f"\n🎤 Fichier audio: {audio_path}")
    
    if subject:
        print(f"📚 Matière sélectionnée: {subject}")
    else:
        print(f"🔍 Détection automatique de la matière...")
    
    print("\n⏳ Traitement en cours...")
    print("   [1/4] Transcription de l'audio (ASR)...")
    print("   [2/4] Recherche de contexte (RAG)...")
    print("   [3/4] Génération de la réponse (LLM)...")
    print("   [4/4] Synthèse vocale (TTS)...")
    
    # Process
    results = orchestrator.process_audio_file(audio_path, subject=subject)
    
    # Display results
    if results.get('success'):
        print_section("✅ RÉSULTATS")
        
        print_result("Temps de traitement", format_time(results.get('processing_time', 0)))
        
        # Transcript
        transcript = results.get('transcript', '')
        print(f"\n📝 Transcription:")
        print(f"   {transcript}")
        
        print_result("Matière détectée", results.get('subject', 'N/A'))
        
        # Sources
        sources = results.get('sources', [])
        if sources:
            print(f"\n📚 Sources utilisées ({len(sources)}):")
            for src in sources:
                print(f"   • {src['filename']} (score: {src['score']:.3f})")
        
        # Response
        print(f"\n💡 Réponse du tuteur:")
        print("-" * 70)
        response = results.get('response', '')
        for line in response.split('\n'):
            print(f"  {line}")
        print("-" * 70)
        
        # Audio output
        audio_output = results.get('audio_output')
        if audio_output:
            print(f"\n🔊 Audio de réponse: {audio_output}")
        
        print_section("✅ DÉMONSTRATION TERMINÉE")
        
    else:
        print_section("❌ ERREUR")
        print(f"\n{results.get('error', 'Erreur inconnue')}")


def demo_interactive(orchestrator: VocalTutorOrchestrator):
    """
    Run interactive demo mode.
    
    Args:
        orchestrator: Orchestrator instance
    """
    print_section("MODE INTERACTIF")
    
    print("\n💬 Posez vos questions! (tapez 'quit' pour quitter)")
    print("   Commandes spéciales:")
    print("   - 'matiere:maths', 'matiere:physique', 'matiere:anglais' : changer de matière")
    print("   - 'history' : afficher l'historique")
    print("   - 'clear' : effacer l'historique")
    print("   - 'status' : afficher le statut")
    
    while True:
        print("\n" + "-" * 70)
        question = input("❓ Votre question: ").strip()
        
        if not question:
            continue
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Au revoir!")
            break
        
        # Handle special commands
        if question.lower().startswith('matiere:'):
            subject = question.split(':')[1].strip()
            try:
                orchestrator.set_subject(subject)
                print(f"✅ Matière changée: {subject}")
            except ValueError as e:
                print(f"❌ {e}")
            continue
        
        if question.lower() == 'history':
            history = orchestrator.get_conversation_history()
            if history:
                print(f"\n📜 Historique ({len(history)} interactions):")
                for i, item in enumerate(history, 1):
                    print(f"\n{i}. [{item['subject']}] {item['timestamp']}")
                    print(f"   Q: {item['question'][:60]}...")
                    print(f"   R: {item['response'][:60]}...")
            else:
                print("\n📜 Historique vide")
            continue
        
        if question.lower() == 'clear':
            orchestrator.clear_history()
            print("✅ Historique effacé")
            continue
        
        if question.lower() == 'status':
            status = orchestrator.get_status()
            print(f"\n📊 Statut:")
            print(f"   Matière actuelle: {status['current_subject']}")
            print(f"   Matières disponibles: {status['available_subjects']}")
            print(f"   Historique: {status['conversation_length']} interactions")
            print(f"   Modules chargés: {sum(status['modules_loaded'].values())}/4")
            continue
        
        # Process question
        print("\n⏳ Traitement...")
        results = orchestrator.process_text_question(question, generate_audio=False)
        
        if results.get('success'):
            print(f"\n📚 Matière: {results.get('subject')}")
            print(f"\n💡 Réponse:")
            print("-" * 70)
            for line in results.get('response', '').split('\n'):
                print(f"  {line}")
            print("-" * 70)
            
            sources = results.get('sources', [])
            if sources:
                print(f"\n📚 Sources: {', '.join(s['filename'] for s in sources)}")
        else:
            print(f"\n❌ Erreur: {results.get('error')}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Demo CLI for Agent Vocal IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:

  # Mode texte
  python demo_cli.py --text "Comment résoudre x² + 2x - 3 = 0 ?" --subject maths
  
  # Mode audio
  python demo_cli.py --audio question.wav
  
  # Mode interactif
  python demo_cli.py --interactive
        """
    )
    
    parser.add_argument('--text', type=str, help="Question en mode texte")
    parser.add_argument('--audio', type=str, help="Fichier audio à traiter")
    parser.add_argument('--subject', type=str, choices=['maths', 'physique', 'anglais'],
                       help="Matière (optionnel, détection auto par défaut)")
    parser.add_argument('--interactive', '-i', action='store_true',
                       help="Mode interactif")
    parser.add_argument('--config', type=str, default='config.yaml',
                       help="Fichier de configuration")
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help="Niveau de log")
    
    args = parser.parse_args()
    
    # Setup
    setup_logging(level=args.log_level)
    
    print_banner()
    
    # Load config
    print("🔧 Chargement de la configuration...")
    config = get_config(args.config)
    
    # Initialize orchestrator
    print("🚀 Initialisation de l'orchestrateur...")
    print("   (Les modèles seront chargés à la demande)")
    orchestrator = VocalTutorOrchestrator(config)
    
    # Check available subjects
    available = orchestrator.get_available_subjects()
    if available:
        print(f"📚 Matières disponibles: {', '.join(available)}")
    else:
        print("⚠️  Aucun indice RAG trouvé. Construisez-les avec:")
        print("   python -m src.rag_build --subject all")
    
    # Run demo based on mode
    if args.interactive:
        demo_interactive(orchestrator)
    elif args.audio:
        if not Path(args.audio).exists():
            print(f"\n❌ Erreur: Fichier audio non trouvé: {args.audio}")
            sys.exit(1)
        demo_audio_mode(orchestrator, args.audio, args.subject)
    elif args.text:
        demo_text_mode(orchestrator, args.text, args.subject)
    else:
        # Default: show help and run simple demo
        print("\n💡 Aucun mode spécifié, démonstration simple:")
        demo_question = "Quelle est la formule pour résoudre une équation du second degré ?"
        demo_text_mode(orchestrator, demo_question, subject='maths')
        print("\n💡 Pour plus d'options, utilisez: python demo_cli.py --help")


if __name__ == "__main__":
    main()
