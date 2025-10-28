#!/usr/bin/env python3
"""Demo CLI for Agent Vocal IA - Offline Voice Tutor"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pipeline import create_pipeline
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def print_banner():
    """Print welcome banner"""
    banner = """
    ╔═══════════════════════════════════════╗
    ║   Agent Vocal IA - Voice Tutor Demo   ║
    ║   ASR → RAG → LLM → TTS Pipeline      ║
    ╚═══════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def check_models():
    """Check if required models exist"""
    models_needed = []
    
    llm_path = "models/llm/model.gguf"
    if not os.path.exists(llm_path):
        models_needed.append(f"LLM model: {llm_path}")
    
    if models_needed:
        console.print("\n[yellow]⚠ Missing models:[/yellow]")
        for model in models_needed:
            console.print(f"  • {model}")
        console.print("\n[cyan]Note:[/cyan] Place your GGUF model in models/llm/")
        return False
    
    return True


def demo_text_mode(pipeline):
    """Run demo in text mode"""
    console.print("\n[green]📝 Text Mode Activated[/green]")
    console.print("Type your questions (or 'quit' to exit)\n")
    
    while True:
        try:
            question = console.input("[bold blue]You:[/bold blue] ")
            
            if question.lower() in ['quit', 'exit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            if not question.strip():
                continue
            
            # Process question
            with console.status("[bold green]Thinking...", spinner="dots"):
                result = pipeline.process_text_query(
                    question=question,
                    use_rag=True,
                    speak_response=False  # No audio in CLI demo
                )
            
            # Display response
            response = result['response']
            console.print(f"\n[bold green]Tutor:[/bold green] {response}\n")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


def demo_audio_mode(pipeline, audio_file):
    """Run demo with audio file"""
    console.print(f"\n[green]🎤 Processing audio file:[/green] {audio_file}")
    
    if not os.path.exists(audio_file):
        console.print(f"[red]Error:[/red] File not found: {audio_file}")
        return
    
    with console.status("[bold green]Processing...", spinner="dots"):
        result = pipeline.process_voice_query(
            audio_path=audio_file,
            language="fr",
            use_rag=True,
            speak_response=False
        )
    
    # Display results
    console.print("\n" + "="*50)
    console.print("[bold cyan]Transcription:[/bold cyan]")
    console.print(result['transcription'])
    console.print("\n[bold green]Response:[/bold green]")
    console.print(result['response'])
    console.print("="*50 + "\n")


def index_documents(pipeline):
    """Index all documents"""
    console.print("\n[cyan]📚 Indexing documents...[/cyan]")
    
    with console.status("[bold green]Indexing...", spinner="dots"):
        pipeline.index_documents()
    
    console.print("[green]✓ Documents indexed successfully![/green]\n")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Agent Vocal IA - Offline Voice Tutor Demo"
    )
    parser.add_argument(
        "--mode",
        choices=["text", "audio"],
        default="text",
        help="Demo mode (text or audio)"
    )
    parser.add_argument(
        "--audio",
        type=str,
        help="Path to audio file (for audio mode)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/llm/model.gguf",
        help="Path to LLM model"
    )
    parser.add_argument(
        "--whisper-size",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        choices=["cuda", "cpu"],
        help="Device for computation"
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="Index documents before running"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check if models exist
    if not os.path.exists(args.model):
        console.print(f"[yellow]⚠ LLM model not found at {args.model}[/yellow]")
        console.print("[cyan]This demo will fail without a model.[/cyan]")
        console.print("[cyan]Download a GGUF model and place it in models/llm/[/cyan]\n")
    
    # Create configuration
    config = {
        "llm_model_path": args.model,
        "whisper_model_size": args.whisper_size,
        "device": args.device,
        "data_dirs": ["data/maths", "data/physique", "data/anglais"],
        "voices_dir": "models/voices"
    }
    
    try:
        console.print("[cyan]Initializing pipeline...[/cyan]")
        
        # Initialize pipeline (may take some time)
        with console.status("[bold green]Loading models...", spinner="dots"):
            pipeline = create_pipeline(config)
        
        console.print("[green]✓ Pipeline ready![/green]\n")
        
        # Index documents if requested
        if args.index:
            index_documents(pipeline)
        
        # Run demo based on mode
        if args.mode == "text":
            demo_text_mode(pipeline)
        elif args.mode == "audio":
            if not args.audio:
                console.print("[red]Error:[/red] --audio required for audio mode")
                sys.exit(1)
            demo_audio_mode(pipeline, args.audio)
        
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("[cyan]Make sure all required models are downloaded.[/cyan]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
