"""
User Interface for Agent Vocal IA using Gradio.

Provides an interactive web interface for the vocal tutoring system.
"""

import logging
import os
import sys
from pathlib import Path

import gradio as gr

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import VocalTutorOrchestrator
from src.utils import get_config, setup_logging


class VocalTutorUI:
    """Gradio UI for Vocal Tutor."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize UI.
        
        Args:
            config_path: Path to configuration file
        """
        # Setup logging
        setup_logging(level='INFO')
        self.logger = logging.getLogger(__name__)
        
        # Load config
        self.config = get_config(config_path)
        
        # Initialize orchestrator (lazy)
        self.orchestrator: VocalTutorOrchestrator = None
        
        # UI configuration
        self.title = self.config.get('ui.title', '🎓 Agent Vocal IA - Tuteur Éducatif')
        self.description = self.config.get('ui.description', 
                                          'Assistant vocal local pour l\'apprentissage (100% offline)')
        self.theme = self.config.get('ui.theme', 'soft')
        
        self.logger.info("Vocal Tutor UI initialized")
    
    def _get_orchestrator(self) -> VocalTutorOrchestrator:
        """Get or create orchestrator instance."""
        if self.orchestrator is None:
            self.logger.info("Loading orchestrator...")
            self.orchestrator = VocalTutorOrchestrator(self.config)
        return self.orchestrator
    
    def process_audio_input(
        self,
        audio_input,
        subject: str,
        auto_detect: bool
    ):
        """
        Process audio input from microphone.
        
        Args:
            audio_input: Audio from Gradio microphone component (tuple of sample_rate, audio_data)
            subject: Selected subject
            auto_detect: Whether to auto-detect subject
            
        Returns:
            Tuple of (transcript, response, sources_text, audio_output, status)
        """
        try:
            self.logger.info("Processing audio input...")
            
            if audio_input is None:
                return ("", "", "", None, "❌ Aucun audio fourni")
            
            # Save audio to temporary file
            import tempfile
            import soundfile as sf
            
            sample_rate, audio_data = audio_input
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name
                sf.write(tmp_path, audio_data, sample_rate)
            
            # Get orchestrator
            orchestrator = self._get_orchestrator()
            
            # Set subject if not auto-detecting
            if not auto_detect and subject:
                orchestrator.set_subject(subject)
            
            # Process
            results = orchestrator.process_audio_file(
                tmp_path,
                subject=None if auto_detect else subject
            )
            
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            
            # Extract results
            if results.get('success'):
                transcript = results.get('transcript', '')
                response = results.get('response', '')
                sources = results.get('sources', [])
                audio_output = results.get('audio_output')
                detected_subject = results.get('subject', '')
                
                # Format sources
                sources_text = self._format_sources(sources)
                
                # Status message
                status = f"✅ Succès! Matière: {detected_subject}"
                
                return (transcript, response, sources_text, audio_output, status)
            else:
                error = results.get('error', 'Erreur inconnue')
                return ("", "", "", None, f"❌ Erreur: {error}")
                
        except Exception as e:
            self.logger.error(f"Error processing audio: {e}", exc_info=True)
            return ("", "", "", None, f"❌ Erreur: {str(e)}")
    
    def process_text_input(
        self,
        text: str,
        subject: str,
        auto_detect: bool,
        generate_audio: bool
    ):
        """
        Process text input.
        
        Args:
            text: Text question
            subject: Selected subject
            auto_detect: Whether to auto-detect subject
            generate_audio: Whether to generate TTS audio
            
        Returns:
            Tuple of (response, sources_text, audio_output, status)
        """
        try:
            if not text or not text.strip():
                return ("", "", None, "❌ Veuillez saisir une question")
            
            self.logger.info(f"Processing text: {text[:50]}...")
            
            # Get orchestrator
            orchestrator = self._get_orchestrator()
            
            # Set subject if not auto-detecting
            if not auto_detect and subject:
                orchestrator.set_subject(subject)
            
            # Process
            results = orchestrator.process_text_question(
                text,
                subject=None if auto_detect else subject,
                generate_audio=generate_audio
            )
            
            # Extract results
            if results.get('success'):
                response = results.get('response', '')
                sources = results.get('sources', [])
                audio_output = results.get('audio_output') if generate_audio else None
                detected_subject = results.get('subject', '')
                
                # Format sources
                sources_text = self._format_sources(sources)
                
                # Status
                status = f"✅ Succès! Matière: {detected_subject}"
                
                return (response, sources_text, audio_output, status)
            else:
                error = results.get('error', 'Erreur inconnue')
                return ("", "", None, f"❌ Erreur: {error}")
                
        except Exception as e:
            self.logger.error(f"Error processing text: {e}", exc_info=True)
            return ("", "", None, f"❌ Erreur: {str(e)}")
    
    def _format_sources(self, sources: list) -> str:
        """Format sources for display."""
        if not sources:
            return "Aucune source trouvée"
        
        lines = ["📚 Sources utilisées:\n"]
        for i, src in enumerate(sources, 1):
            filename = src.get('filename', 'Inconnu')
            score = src.get('score', 0)
            lines.append(f"{i}. {filename} (score: {score:.3f})")
        
        return "\n".join(lines)
    
    def get_available_subjects(self):
        """Get list of available subjects."""
        try:
            orchestrator = self._get_orchestrator()
            subjects = orchestrator.get_available_subjects()
            return subjects if subjects else ['maths', 'physique', 'anglais']
        except Exception:
            return ['maths', 'physique', 'anglais']
    
    def build_interface(self) -> gr.Blocks:
        """
        Build Gradio interface.
        
        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks(title=self.title, theme=self.theme) as interface:
            # Header
            gr.Markdown(f"# {self.title}")
            gr.Markdown(f"*{self.description}*")
            
            # Get available subjects
            available_subjects = self.get_available_subjects()
            
            # Settings row
            with gr.Row():
                subject_selector = gr.Dropdown(
                    choices=available_subjects,
                    value=available_subjects[0] if available_subjects else 'maths',
                    label="📚 Matière",
                    info="Sélectionnez la matière"
                )
                auto_detect_checkbox = gr.Checkbox(
                    value=True,
                    label="🔍 Détection automatique",
                    info="Détecte la matière depuis la question"
                )
            
            # Main tabs
            with gr.Tabs():
                # Tab 1: Audio Input
                with gr.Tab("🎤 Mode Vocal"):
                    gr.Markdown("### Posez votre question vocalement")
                    
                    with gr.Row():
                        audio_input = gr.Audio(
                            sources=["microphone"],
                            type="numpy",
                            label="🎤 Enregistrement audio"
                        )
                    
                    process_audio_btn = gr.Button("🚀 Traiter l'audio", variant="primary")
                    
                    with gr.Row():
                        transcript_output = gr.Textbox(
                            label="📝 Transcription",
                            lines=3,
                            interactive=False
                        )
                    
                    with gr.Row():
                        response_output_audio = gr.Textbox(
                            label="💡 Réponse du tuteur",
                            lines=8,
                            interactive=False
                        )
                    
                    with gr.Row():
                        sources_output_audio = gr.Textbox(
                            label="📚 Sources",
                            lines=3,
                            interactive=False
                        )
                    
                    with gr.Row():
                        audio_output = gr.Audio(
                            label="🔊 Réponse vocale",
                            type="filepath"
                        )
                    
                    status_audio = gr.Textbox(
                        label="📊 Statut",
                        interactive=False
                    )
                    
                    # Connect audio processing
                    process_audio_btn.click(
                        fn=self.process_audio_input,
                        inputs=[audio_input, subject_selector, auto_detect_checkbox],
                        outputs=[transcript_output, response_output_audio, 
                                sources_output_audio, audio_output, status_audio]
                    )
                
                # Tab 2: Text Input
                with gr.Tab("💬 Mode Texte"):
                    gr.Markdown("### Posez votre question par écrit")
                    
                    text_input = gr.Textbox(
                        label="✏️ Votre question",
                        placeholder="Ex: Comment résoudre une équation du second degré ?",
                        lines=3
                    )
                    
                    generate_audio_checkbox = gr.Checkbox(
                        value=True,
                        label="🔊 Générer l'audio",
                        info="Synthétiser la réponse en audio"
                    )
                    
                    process_text_btn = gr.Button("🚀 Envoyer", variant="primary")
                    
                    with gr.Row():
                        response_output_text = gr.Textbox(
                            label="💡 Réponse du tuteur",
                            lines=10,
                            interactive=False
                        )
                    
                    with gr.Row():
                        sources_output_text = gr.Textbox(
                            label="📚 Sources",
                            lines=3,
                            interactive=False
                        )
                    
                    with gr.Row():
                        audio_output_text = gr.Audio(
                            label="🔊 Réponse vocale",
                            type="filepath"
                        )
                    
                    status_text = gr.Textbox(
                        label="📊 Statut",
                        interactive=False
                    )
                    
                    # Connect text processing
                    process_text_btn.click(
                        fn=self.process_text_input,
                        inputs=[text_input, subject_selector, auto_detect_checkbox, 
                               generate_audio_checkbox],
                        outputs=[response_output_text, sources_output_text, 
                                audio_output_text, status_text]
                    )
            
            # Footer
            gr.Markdown("---")
            gr.Markdown(
                "💡 **Conseil**: Le système fournit des indices progressifs pour vous aider "
                "à comprendre par vous-même. Ne vous attendez pas à une réponse complète directe!"
            )
            gr.Markdown(
                "🔧 **Note**: Tous les modèles fonctionnent localement (offline). "
                "La première utilisation peut prendre quelques secondes pour charger les modèles."
            )
        
        return interface
    
    def launch(
        self,
        share: bool = False,
        server_port: int = None,
        server_name: str = None
    ):
        """
        Launch Gradio interface.
        
        Args:
            share: Create public link
            server_port: Server port
            server_name: Server name/IP
        """
        port = server_port or self.config.get('ui.server_port', 7860)
        share = share or self.config.get('ui.share', False)
        
        interface = self.build_interface()
        
        self.logger.info(f"Launching UI on port {port} (share={share})")
        
        interface.launch(
            share=share,
            server_port=port,
            server_name=server_name,
            show_error=True
        )


def launch_ui(config_path: str = "config.yaml", share: bool = False):
    """
    Convenience function to launch UI.
    
    Args:
        config_path: Path to config file
        share: Create public link
    """
    ui = VocalTutorUI(config_path)
    ui.launch(share=share)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Launch Vocal Tutor UI")
    parser.add_argument('--config', type=str, default='config.yaml', help="Config file")
    parser.add_argument('--share', action='store_true', help="Create public link")
    parser.add_argument('--port', type=int, default=7860, help="Server port")
    
    args = parser.parse_args()
    
    ui = VocalTutorUI(args.config)
    ui.launch(share=args.share, server_port=args.port)
