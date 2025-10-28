"""Gradio Web Interface for Agent Vocal IA"""

import gradio as gr
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.pipeline import create_pipeline


class VoiceTutorInterface:
    """Gradio interface for the voice tutor"""
    
    def __init__(self, pipeline):
        """Initialize interface with pipeline
        
        Args:
            pipeline: VoiceTutorPipeline instance
        """
        self.pipeline = pipeline
    
    def process_text_input(self, text, use_rag):
        """Process text input
        
        Args:
            text: User question
            use_rag: Whether to use RAG
            
        Returns:
            Response text
        """
        if not text.strip():
            return "Please enter a question."
        
        result = self.pipeline.process_text_query(
            question=text,
            use_rag=use_rag,
            speak_response=False
        )
        
        return result['response']
    
    def process_audio_input(self, audio, language, use_rag):
        """Process audio input
        
        Args:
            audio: Audio file path
            language: Language code
            use_rag: Whether to use RAG
            
        Returns:
            Tuple of (transcription, response)
        """
        if audio is None:
            return "No audio provided", ""
        
        result = self.pipeline.process_voice_query(
            audio_path=audio,
            language=language,
            use_rag=use_rag,
            speak_response=False
        )
        
        return result['transcription'], result['response']
    
    def reset_chat(self):
        """Reset conversation"""
        self.pipeline.reset_conversation()
        return "Conversation reset!"
    
    def create_interface(self):
        """Create Gradio interface
        
        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks(title="Agent Vocal IA") as interface:
            gr.Markdown("""
            # 🎓 Agent Vocal IA - Offline Voice Tutor
            
            An intelligent tutoring system for Mathematics, Physics, and English.
            Features ASR → RAG → LLM → TTS pipeline running offline.
            """)
            
            with gr.Tab("Text Mode"):
                with gr.Row():
                    with gr.Column():
                        text_input = gr.Textbox(
                            label="Your Question",
                            placeholder="Ask a question about maths, physics, or English...",
                            lines=3
                        )
                        text_rag_checkbox = gr.Checkbox(
                            label="Use RAG (Retrieve course materials)",
                            value=True
                        )
                        text_submit_btn = gr.Button("Submit", variant="primary")
                        text_clear_btn = gr.Button("Clear")
                    
                    with gr.Column():
                        text_output = gr.Textbox(
                            label="Tutor Response",
                            lines=10
                        )
                
                text_submit_btn.click(
                    fn=self.process_text_input,
                    inputs=[text_input, text_rag_checkbox],
                    outputs=text_output
                )
                text_clear_btn.click(
                    fn=lambda: "",
                    outputs=text_output
                )
            
            with gr.Tab("Voice Mode"):
                with gr.Row():
                    with gr.Column():
                        audio_input = gr.Audio(
                            label="Record or Upload Audio",
                            source="microphone",
                            type="filepath"
                        )
                        audio_language = gr.Dropdown(
                            choices=["fr", "en"],
                            value="fr",
                            label="Language"
                        )
                        audio_rag_checkbox = gr.Checkbox(
                            label="Use RAG",
                            value=True
                        )
                        audio_submit_btn = gr.Button("Process Audio", variant="primary")
                    
                    with gr.Column():
                        transcription_output = gr.Textbox(
                            label="Transcription",
                            lines=3
                        )
                        audio_response_output = gr.Textbox(
                            label="Tutor Response",
                            lines=10
                        )
                
                audio_submit_btn.click(
                    fn=self.process_audio_input,
                    inputs=[audio_input, audio_language, audio_rag_checkbox],
                    outputs=[transcription_output, audio_response_output]
                )
            
            with gr.Tab("Settings"):
                gr.Markdown("""
                ### System Information
                
                - **ASR**: faster-whisper + silero-vad
                - **RAG**: FAISS + SentenceTransformers
                - **LLM**: llama-cpp-python (local)
                - **TTS**: piper-tts
                
                ### Data Sources
                
                - Mathematics: `data/maths/`
                - Physics: `data/physique/`
                - English: `data/anglais/`
                """)
                
                reset_btn = gr.Button("Reset Conversation")
                reset_output = gr.Textbox(label="Status")
                
                reset_btn.click(
                    fn=self.reset_chat,
                    outputs=reset_output
                )
        
        return interface


def launch_interface(config=None):
    """Launch Gradio interface
    
    Args:
        config: Optional pipeline configuration
    """
    print("Initializing pipeline...")
    pipeline = create_pipeline(config)
    
    print("Creating interface...")
    tutor_interface = VoiceTutorInterface(pipeline)
    interface = tutor_interface.create_interface()
    
    print("Launching interface...")
    interface.launch(share=False)


if __name__ == "__main__":
    launch_interface()
