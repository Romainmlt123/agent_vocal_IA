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
from src.conversation_manager import ConversationManager
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
        
        # Initialize conversation manager (lazy)
        self.conversation_manager: ConversationManager = None
        
        # Conversation state
        self.conversation_history = []
        self.conversation_active = False
        
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
    
    def _get_conversation_manager(self) -> ConversationManager:
        """Get or create conversation manager instance."""
        if self.conversation_manager is None:
            self.logger.info("Loading conversation manager...")
            orchestrator = self._get_orchestrator()
            self.conversation_manager = ConversationManager(self.config, orchestrator)
        return self.conversation_manager
    
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
    
    def toggle_conversation(
        self,
        current_state: bool,
        subject: str,
        auto_detect: bool
    ):
        """
        Toggle conversation mode on/off.
        
        Args:
            current_state: Current conversation state
            subject: Selected subject
            auto_detect: Whether to auto-detect subject
            
        Returns:
            Tuple of (new_state, button_text, button_variant, status_message, transcript, response)
        """
        try:
            if not current_state:
                # Start conversation
                self.logger.info("Starting continuous conversation...")
                
                # Get conversation manager
                conv_mgr = self._get_conversation_manager()
                
                # Set subject if not auto-detecting
                if not auto_detect and subject:
                    self._get_orchestrator().set_subject(subject)
                
                # Clear previous history for this session
                self.conversation_history = []
                
                # Start conversation
                conv_mgr.start_conversation()
                
                return (
                    True,  # new state
                    "🛑 Arrêter la conversation",
                    "stop",
                    "🎤 Conversation active! Parlez naturellement, l'IA détectera automatiquement quand vous avez fini de parler.",
                    "",  # transcript
                    ""   # response
                )
            
            else:
                # Stop conversation
                self.logger.info("Stopping continuous conversation...")
                
                conv_mgr = self._get_conversation_manager()
                conv_mgr.stop_conversation()
                
                return (
                    False,  # new state
                    "🎤 Démarrer la conversation",
                    "primary",
                    "✅ Conversation terminée. Cliquez pour recommencer.",
                    "",  # transcript
                    ""   # response
                )
        
        except Exception as e:
            self.logger.error(f"Error toggling conversation: {e}", exc_info=True)
            return (
                False,
                "🎤 Démarrer la conversation",
                "primary",
                f"❌ Erreur: {str(e)}",
                "",
                ""
            )
    
    def poll_conversation_updates(self, is_active: bool):
        """
        Poll for conversation updates (for real-time display).
        
        Args:
            is_active: Whether conversation is active
            
        Returns:
            Tuple of (transcript, response, history, status)
        """
        if not is_active:
            return ("", "", self.get_conversation_history(), "")
        
        try:
            conv_mgr = self._get_conversation_manager()
            results = conv_mgr.get_latest_results()
            
            transcript = results.get('transcript', '')
            response = results.get('response', '')
            status = results.get('status', '')
            
            # Update history if we have new results
            if transcript and response:
                # Check if this is a new entry
                if not self.conversation_history or \
                   self.conversation_history[-1].get('user') != transcript:
                    self.conversation_history.append({
                        'user': transcript,
                        'ai': response
                    })
            
            history = self.get_conversation_history()
            
            return (transcript, response, history, status)
            
        except Exception as e:
            self.logger.error(f"Error polling updates: {e}")
            return ("", "", self.get_conversation_history(), f"❌ Erreur: {str(e)}")
    
    def get_conversation_history(self):
        """Get formatted conversation history."""
        if not self.conversation_history:
            return "Aucun historique de conversation"
        
        lines = ["📜 Historique de la conversation:\n"]
        for i, entry in enumerate(self.conversation_history, 1):
            user_text = entry.get('user', '')
            ai_text = entry.get('ai', '')
            lines.append(f"\n**Tour {i}:**")
            lines.append(f"👤 Vous: {user_text}")
            lines.append(f"🤖 IA: {ai_text}")
        
        return "\n".join(lines)
    
    def clear_conversation_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        return "✅ Historique effacé"
    
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
                # Tab 1: Continuous Conversation (NEW!)
                with gr.Tab("💬 Conversation Continue"):
                    gr.Markdown("""
                    ### 🎤 Mode Conversation Naturelle
                    
                    **Comment ça marche ?**
                    1. Cliquez sur "Démarrer la conversation" 🎤
                    2. Parlez naturellement (pas besoin de cliquer à nouveau)
                    3. L'IA détecte automatiquement quand vous avez fini de parler
                    4. L'IA répond vocalement
                    5. Vous pouvez immédiatement continuer à parler
                    6. Cliquez sur "Arrêter" quand vous avez terminé 🛑
                    
                    **⚡ Détection automatique de fin de parole par VAD (Voice Activity Detection)**
                    """)
                    
                    # Conversation state
                    conversation_state = gr.State(value=False)
                    
                    with gr.Row():
                        toggle_conversation_btn = gr.Button(
                            "🎤 Démarrer la conversation",
                            variant="primary",
                            size="lg"
                        )
                    
                    status_conversation = gr.Textbox(
                        label="📊 Statut",
                        value="Prêt à démarrer",
                        interactive=False,
                        lines=2
                    )
                    
                    with gr.Row():
                        with gr.Column():
                            conversation_transcript = gr.Textbox(
                                label="📝 Dernière transcription",
                                lines=3,
                                interactive=False
                            )
                        
                        with gr.Column():
                            conversation_response = gr.Textbox(
                                label="💡 Dernière réponse IA",
                                lines=6,
                                interactive=False
                            )
                    
                    conversation_history_display = gr.Textbox(
                        label="📜 Historique de la conversation",
                        lines=10,
                        interactive=False
                    )
                    
                    with gr.Row():
                        refresh_history_btn = gr.Button("🔄 Actualiser l'historique")
                        clear_history_btn = gr.Button("🗑️ Effacer l'historique")
                    
                    # Connect conversation toggle
                    toggle_conversation_btn.click(
                        fn=self.toggle_conversation,
                        inputs=[conversation_state, subject_selector, auto_detect_checkbox],
                        outputs=[conversation_state, toggle_conversation_btn, 
                                toggle_conversation_btn, status_conversation,
                                conversation_transcript, conversation_response]
                    )
                    
                    # Polling for updates (every 2 seconds when active)
                    # Note: Gradio doesn't support true push updates, so we poll
                    def update_loop():
                        import time
                        while True:
                            time.sleep(2)
                            yield self.poll_conversation_updates(conversation_state.value)
                    
                    # Auto-refresh conversation display
                    conversation_state.change(
                        fn=self.poll_conversation_updates,
                        inputs=[conversation_state],
                        outputs=[conversation_transcript, conversation_response,
                                conversation_history_display, status_conversation],
                        every=2  # Poll every 2 seconds
                    )
                    
                    # Connect history buttons
                    refresh_history_btn.click(
                        fn=self.get_conversation_history,
                        outputs=conversation_history_display
                    )
                    
                    clear_history_btn.click(
                        fn=self.clear_conversation_history,
                        outputs=status_conversation
                    )
                
                # Tab 2: Audio Input (Manuel)
                with gr.Tab("🎤 Mode Vocal Manuel"):
                    gr.Markdown("### Posez votre question vocalement (enregistrement manuel)")
                    gr.Markdown("*Cliquez pour démarrer l'enregistrement, puis cliquez à nouveau pour l'arrêter*")
                    
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
                
                # Tab 3: Text Input
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
