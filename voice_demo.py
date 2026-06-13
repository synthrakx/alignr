# voice_demo.py — Raj's Dental Clinic AI Receptionist
# Pipecat 1.2.1 + WhisperSTT + qwen3:8b + KokoroTTS
# Record with Windows Game Bar (Win+G) or OBS

import asyncio
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask, PipelineParams
from pipecat.services.ollama.llm import OLLamaLLMService
from pipecat.services.kokoro.tts import KokoroTTSService
from pipecat.services.whisper.stt import WhisperSTTService
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

SYSTEM_PROMPT = """You are the AI receptionist for Raj's Dental Clinic.
You handle appointment booking, FAQ questions, and after-hours inquiries.
Clinic hours: Monday-Saturday 9 AM to 7 PM.
Services: cleanings, fillings, extractions, whitening.
Be warm, professional, and concise — maximum 2 sentences per response.
If someone wants to book: ask their name, preferred day, and best phone number."""

async def main():
    transport = LocalAudioTransport(LocalAudioTransportParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        audio_in_device_index=2
    ))

    stt = WhisperSTTService()
    llm = OLLamaLLMService(model="qwen3:8b", system=SYSTEM_PROMPT)
    tts = KokoroTTSService(voice="af_heart")

    pipeline = Pipeline([
        transport.input(),
        stt,
        llm,
        tts,
        transport.output(),
    ])

    task = PipelineTask(pipeline, params=PipelineParams(allow_interruptions=True))
    runner = PipelineRunner()

    print("=== Raj's Dental Clinic — AI Receptionist Demo ===")
    print("Microphone: Headset (Nirvana Ion)")
    print("Start recording NOW (Win+G or OBS)")
    print("Speak immediately when pipeline is ready")
    print("Press Ctrl+C to end")
    await runner.run(task)

asyncio.run(main())