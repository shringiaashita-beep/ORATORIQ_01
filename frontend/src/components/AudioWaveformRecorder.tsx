"use client";

import React, { useState, useRef, useEffect } from "react";

export interface AudioWaveformRecorderProps {
  onEvaluateAudio: (formData: FormData) => Promise<void>;
  onEvaluateTranscript: (transcript: string) => Promise<void>;
  isEvaluating?: boolean;
}

export function AudioWaveformRecorder({
  onEvaluateAudio,
  onEvaluateTranscript,
  isEvaluating = false,
}: AudioWaveformRecorderProps) {
  const [inputMode, setInputMode] = useState<"mic" | "upload" | "text">("mic");

  // Mic recording states
  const [isRecording, setIsRecording] = useState(false);
  const [recordSeconds, setRecordSeconds] = useState(0);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [recordedUrl, setRecordedUrl] = useState<string | null>(null);

  // File upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Transcript input (for transcript-only mode OR optional paired transcript for audio alignment)
  const [transcriptText, setTranscriptText] = useState<string>("");

  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const speechRecognitionRef = useRef<any>(null);
  const [liveSpeechDetected, setLiveSpeechDetected] = useState<boolean>(false);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      if (audioContextRef.current && audioContextRef.current.state !== "closed") {
        audioContextRef.current.close().catch(() => {});
      }
    };
  }, []);

  // Format seconds to mm:ss
  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60)
      .toString()
      .padStart(2, "0");
    const s = (secs % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  // Convert Web Audio API AudioBuffer to standard 16-bit PCM WAV
  const audioBufferToWav = (buffer: AudioBuffer): Blob => {
    const numChannels = 1;
    const sampleRate = buffer.sampleRate;
    const format = 1; // PCM
    const bitDepth = 16;

    let channelData: Float32Array;
    if (buffer.numberOfChannels > 1) {
      const ch0 = buffer.getChannelData(0);
      const ch1 = buffer.getChannelData(1);
      channelData = new Float32Array(buffer.length);
      for (let i = 0; i < buffer.length; i++) {
        channelData[i] = (ch0[i] + ch1[i]) / 2;
      }
    } else {
      channelData = buffer.getChannelData(0);
    }

    const bytesPerSample = bitDepth / 8;
    const blockAlign = numChannels * bytesPerSample;
    const dataSize = channelData.length * bytesPerSample;
    const bufferSize = 44 + dataSize;
    const arrayBuffer = new ArrayBuffer(bufferSize);
    const view = new DataView(arrayBuffer);

    // RIFF identifier
    view.setUint32(0, 0x52494646, false); // "RIFF"
    view.setUint32(4, 36 + dataSize, true); // file length - 8
    view.setUint32(8, 0x57415645, false); // "WAVE"
    // fmt sub-chunk
    view.setUint32(12, 0x666d7420, false); // "fmt "
    view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
    view.setUint16(20, format, true); // AudioFormat
    view.setUint16(22, numChannels, true); // NumChannels
    view.setUint32(24, sampleRate, true); // SampleRate
    view.setUint32(28, sampleRate * blockAlign, true); // ByteRate
    view.setUint16(32, blockAlign, true); // BlockAlign
    view.setUint16(34, bitDepth, true); // BitsPerSample
    // data sub-chunk
    view.setUint32(36, 0x64617461, false); // "data"
    view.setUint32(40, dataSize, true); // Subchunk2Size

    let offset = 44;
    for (let i = 0; i < channelData.length; i++) {
      const s = Math.max(-1, Math.min(1, channelData[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
      offset += 2;
    }

    return new Blob([view], { type: "audio/wav" });
  };

  // Live Canvas Waveform Draw Loop
  const drawWaveform = () => {
    if (!canvasRef.current || !analyserRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const analyser = analyserRef.current;
    const bufferLength = analyser.fftSize;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteTimeDomainData(dataArray);

    ctx.fillStyle = "#0E1626";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.lineWidth = 2.5;
    ctx.strokeStyle = "#06B6D4";
    ctx.beginPath();

    const sliceWidth = canvas.width / bufferLength;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const v = dataArray[i] / 128.0;
      const y = (v * canvas.height) / 2;

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
      x += sliceWidth;
    }

    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();

    animFrameRef.current = requestAnimationFrame(drawWaveform);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];

      // Audio analyser setup
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 512;
      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      audioContextRef.current = audioCtx;
      analyserRef.current = analyser;

      drawWaveform();

      // MediaRecorder setup
      const recorder = new MediaRecorder(stream);
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        const rawBlob = new Blob(audioChunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        });

        try {
          const arrayBuffer = await rawBlob.arrayBuffer();
          const decodeCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
          const audioBuffer = await decodeCtx.decodeAudioData(arrayBuffer);
          const wavBlob = audioBufferToWav(audioBuffer);
          decodeCtx.close().catch(() => {});

          const url = URL.createObjectURL(wavBlob);
          setRecordedUrl(url);
          setRecordedBlob(wavBlob);
        } catch (e) {
          const url = URL.createObjectURL(rawBlob);
          setRecordedUrl(url);
          setRecordedBlob(rawBlob);
        }

        // Stop tracks
        stream.getTracks().forEach((track) => track.stop());
        if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      };

      // Web Speech API live speech recognition
      if (typeof window !== "undefined") {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (SpeechRecognition) {
          try {
            const recognizer = new SpeechRecognition();
            recognizer.continuous = true;
            recognizer.interimResults = true;
            recognizer.lang = "en-US";
            recognizer.onresult = (event: any) => {
              let textAccumulator = "";
              for (let i = 0; i < event.results.length; i++) {
                textAccumulator += event.results[i][0].transcript + " ";
              }
              const cleanText = textAccumulator.trim();
              if (cleanText) {
                setTranscriptText(cleanText);
                setLiveSpeechDetected(true);
              }
            };
            recognizer.onerror = () => {};
            recognizer.start();
            speechRecognitionRef.current = recognizer;
          } catch (e) {
            // SpeechRecognition fallback
          }
        }
      }

      recorder.start(250);
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
      setRecordSeconds(0);

      timerIntervalRef.current = setInterval(() => {
        setRecordSeconds((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      alert("Microphone permission denied or microphone not found.");
    }
  };

  const stopRecording = () => {
    if (speechRecognitionRef.current) {
      try {
        speechRecognitionRef.current.stop();
      } catch (e) {}
      speechRecognitionRef.current = null;
    }

    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    }
  };

  const resetRecording = () => {
    if (speechRecognitionRef.current) {
      try {
        speechRecognitionRef.current.stop();
      } catch (e) {}
      speechRecognitionRef.current = null;
    }
    setLiveSpeechDetected(false);
    if (isRecording) stopRecording();
    setRecordedBlob(null);
    setRecordedUrl(null);
    setRecordSeconds(0);

    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext("2d");
      if (ctx) {
        ctx.fillStyle = "#0E1626";
        ctx.fillRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
    }
  };

  const clearSelectedFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmit = async () => {
    if (inputMode === "text") {
      if (!transcriptText.trim()) {
        alert("Please enter speech transcript text to evaluate.");
        return;
      }
      await onEvaluateTranscript(transcriptText);
      return;
    }

    const formData = new FormData();

    if (inputMode === "mic") {
      if (!recordedBlob) {
        alert("Please record audio before evaluating.");
        return;
      }
      const isWav = recordedBlob.type.includes("wav");
      const filename = isWav ? "mic_recording.wav" : "mic_recording.webm";
      const mime = isWav ? "audio/wav" : (recordedBlob.type || "audio/webm");
      const audioFile = new File([recordedBlob], filename, {
        type: mime,
      });
      formData.append("file", audioFile);
      formData.append("audio_file", audioFile);
    } else if (inputMode === "upload") {
      if (!selectedFile) {
        alert("Please select or drop an audio file.");
        return;
      }
      formData.append("file", selectedFile);
      formData.append("audio_file", selectedFile);
    }

    if (transcriptText.trim()) {
      formData.append("transcript", transcriptText.trim());
    }

    await onEvaluateAudio(formData);
  };

  return (
    <div className="flex flex-col space-y-5">
      {/* Input Mode Selector */}
      <div className="flex items-center space-x-2 bg-[#0E1626] p-1.5 rounded-2xl border border-[#1E2E4A]">
        <button
          onClick={() => setInputMode("mic")}
          className={`flex-1 flex items-center justify-center space-x-2 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
            inputMode === "mic"
              ? "bg-[#1E2E4A] text-white border border-[#2E456E] shadow-sm"
              : "text-[#94A3B8] hover:text-white hover:bg-[#131E33]"
          }`}
        >
          <svg viewBox="0 0 24 24" className="w-4 h-4 text-[#F43F5E]" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
          </svg>
          <span>Live Microphone</span>
        </button>

        <button
          onClick={() => setInputMode("upload")}
          className={`flex-1 flex items-center justify-center space-x-2 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
            inputMode === "upload"
              ? "bg-[#1E2E4A] text-white border border-[#2E456E] shadow-sm"
              : "text-[#94A3B8] hover:text-white hover:bg-[#131E33]"
          }`}
        >
          <svg viewBox="0 0 24 24" className="w-4 h-4 text-[#06B6D4]" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          <span>Audio File Upload</span>
        </button>

        <button
          onClick={() => setInputMode("text")}
          className={`flex-1 flex items-center justify-center space-x-2 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
            inputMode === "text"
              ? "bg-[#1E2E4A] text-white border border-[#2E456E] shadow-sm"
              : "text-[#94A3B8] hover:text-white hover:bg-[#131E33]"
          }`}
        >
          <svg viewBox="0 0 24 24" className="w-4 h-4 text-[#818CF8]" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          <span>Transcript-Only Mode</span>
        </button>
      </div>

      {/* Mode A: Live Mic Recording */}
      {inputMode === "mic" && (
        <div className="bg-[#0E1626] border border-[#1E2E4A] rounded-2xl p-6 shadow-xl space-y-4">
          <div className="relative w-full h-28 bg-[#0A0F1D] rounded-xl overflow-hidden border border-[#1E2E4A] flex items-center justify-center">
            <canvas ref={canvasRef} width={700} height={112} className="w-full h-full" />
            <div className="absolute top-2.5 right-3 font-mono text-xs font-bold px-2.5 py-1 rounded-lg bg-[#080C16]/90 text-[#06B6D4] border border-[#1E2E4A]">
              {formatTime(recordSeconds)}
            </div>
            {!isRecording && !recordedBlob && (
              <div className="absolute text-xs text-[#64748B] pointer-events-none">
                Microphone idle • Press &quot;Start Recording&quot; below
              </div>
            )}
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center space-x-3">
              {!isRecording ? (
                <button
                  onClick={startRecording}
                  className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-[#F43F5E] to-[#E11D48] text-white font-semibold text-xs shadow-md shadow-[#F43F5E]/20 hover:opacity-90 transition-all cursor-pointer"
                >
                  <span className="w-2.5 h-2.5 rounded-full bg-white animate-pulse"></span>
                  <span>Start Recording</span>
                </button>
              ) : (
                <button
                  onClick={stopRecording}
                  className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-[#F59E0B] text-black font-semibold text-xs hover:bg-[#FBBF24] transition-all cursor-pointer"
                >
                  <span className="w-2.5 h-2.5 bg-black"></span>
                  <span>Stop Recording</span>
                </button>
              )}

              <button
                onClick={resetRecording}
                disabled={!recordedBlob && !isRecording}
                className="px-4 py-2.5 rounded-xl bg-[#131E33] border border-[#1E2E4A] text-[#94A3B8] hover:text-white disabled:opacity-40 text-xs font-medium transition-all"
              >
                Reset
              </button>
            </div>

            <div className="text-xs text-[#64748B] font-mono flex items-center space-x-2">
              {isRecording ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-[#10B981] animate-ping"></span>
                  <span className="text-[#34D399]">
                    {liveSpeechDetected ? "Live Speech-To-Text Active" : "Recording speech stream..."}
                  </span>
                </>
              ) : recordedBlob ? (
                <span className="text-[#38BDF8]">✓ Audio captured & ready</span>
              ) : (
                <span>Live Speech Recognition enabled • Max 10 mins</span>
              )}
            </div>
          </div>

          {/* Captured Audio Preview */}
          {recordedBlob && recordedUrl && (
            <div className="p-3.5 bg-[#0A0F1D] border border-[#1E2E4A] rounded-xl space-y-2">
              <span className="text-xs font-semibold text-[#94A3B8]">Recorded Audio Preview:</span>
              <audio src={recordedUrl} controls className="w-full h-9 rounded-lg" />
            </div>
          )}

          {/* Optional Transcript Input for Alignment */}
          <div className="space-y-1.5 pt-2 border-t border-[#1E2E4A]/60">
            <label className="text-[11px] font-semibold text-[#94A3B8] flex items-center justify-between">
              <span>Speech Transcript (Auto-transcribed live via Web Speech API or built-in speech engine):</span>
              {liveSpeechDetected && (
                <span className="text-[10px] text-[#34D399] font-mono font-bold">✓ Live Transcribed</span>
              )}
            </label>
            <textarea
              rows={3}
              value={transcriptText}
              onChange={(e) => setTranscriptText(e.target.value)}
              placeholder="Paste or write the spoken words to verify acoustic word boundaries..."
              className="w-full bg-[#131E33] border border-[#1E2E4A] rounded-xl p-3 text-xs text-white placeholder-[#64748B] focus:outline-none focus:border-[#6366F1]"
            />
          </div>
        </div>
      )}

      {/* Mode B: File Upload */}
      {inputMode === "upload" && (
        <div className="bg-[#0E1626] border border-[#1E2E4A] rounded-2xl p-6 shadow-xl space-y-4">
          {!selectedFile ? (
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-[#2E456E] hover:border-[#06B6D4] bg-[#0A0F1D]/60 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all"
            >
              <div className="w-12 h-12 rounded-xl bg-[#131E33] flex items-center justify-center text-[#06B6D4] mb-3">
                <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
              </div>
              <p className="text-xs font-bold text-white">Click or drag & drop an audio file here</p>
              <p className="text-[11px] text-[#64748B] mt-1">
                Supports WAV, MP3, WebM, OGG, FLAC (Max 50MB, decoded via librosa/soundfile)
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*,.wav,.mp3,.webm,.ogg,.flac"
                className="hidden"
                onChange={handleFileChange}
              />
            </div>
          ) : (
            <div className="flex items-center justify-between p-4 bg-[#0A0F1D] border border-[#1E2E4A] rounded-xl">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-[#06B6D4]/20 text-[#06B6D4] flex items-center justify-center">
                  <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M9 18V5l12-2v13"></path>
                    <circle cx="6" cy="18" r="3"></circle>
                    <circle cx="18" cy="16" r="3"></circle>
                  </svg>
                </div>
                <div>
                  <div className="text-xs font-bold text-white">{selectedFile.name}</div>
                  <div className="text-[11px] text-[#64748B]">
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • File validated
                  </div>
                </div>
              </div>

              <button
                onClick={clearSelectedFile}
                className="px-3 py-1.5 rounded-lg bg-[#1E2E4A] hover:bg-[#F43F5E]/20 text-[#94A3B8] hover:text-[#F43F5E] text-xs font-medium transition-colors"
              >
                Remove
              </button>
            </div>
          )}

          {/* Optional Transcript Input for Alignment */}
          <div className="space-y-1.5 pt-2 border-t border-[#1E2E4A]/60">
            <label className="text-[11px] font-semibold text-[#94A3B8]">
              Speech Transcript (Optional — aligns speech if provided; Whisper aligner used otherwise):
            </label>
            <textarea
              rows={3}
              value={transcriptText}
              onChange={(e) => setTranscriptText(e.target.value)}
              placeholder="Paste or write the spoken speech text..."
              className="w-full bg-[#131E33] border border-[#1E2E4A] rounded-xl p-3 text-xs text-white placeholder-[#64748B] focus:outline-none focus:border-[#6366F1]"
            />
          </div>
        </div>
      )}

      {/* Mode C: Transcript Only Mode */}
      {inputMode === "text" && (
        <div className="bg-[#0E1626] border border-[#1E2E4A] rounded-2xl p-6 shadow-xl space-y-4">
          <div className="bg-[#131E33] border border-[#F59E0B]/30 rounded-xl p-3.5 flex items-start space-x-3">
            <div className="p-1.5 rounded-lg bg-[#F59E0B]/10 text-[#F59E0B] shrink-0 mt-0.5">
              <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
            </div>
            <div>
              <h5 className="text-xs font-bold text-white">Transcript-Only Evaluation Mode Active</h5>
              <p className="text-[11px] text-[#94A3B8] mt-0.5">
                Vocal Delivery will be reported as <strong>UNAVAILABLE</strong> (never fabricated with default numbers). Overall score will be normalized exclusively over evaluated criteria.
              </p>
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs text-[#94A3B8]">
              <span className="font-semibold text-white">Enter Complete Speech Transcript:</span>
              <span className="font-mono text-[11px] text-[#64748B]">
                {transcriptText.split(/\s+/).filter(Boolean).length} words
              </span>
            </div>
            <textarea
              rows={7}
              value={transcriptText}
              onChange={(e) => setTranscriptText(e.target.value)}
              placeholder="Paste speech transcript here (e.g. speeches from keynotes, interviews, pitches)..."
              className="w-full bg-[#131E33] border border-[#1E2E4A] rounded-xl p-3.5 text-xs text-white leading-relaxed placeholder-[#64748B] focus:outline-none focus:border-[#6366F1]"
            />
          </div>
        </div>
      )}

      {/* Primary Action Button */}
      <button
        onClick={handleSubmit}
        disabled={isEvaluating}
        className="w-full py-3.5 rounded-xl bg-gradient-to-r from-[#6366F1] via-[#38BDF8] to-[#06B6D4] text-white text-sm font-bold shadow-lg shadow-[#6366F1]/20 hover:opacity-95 transition-all cursor-pointer disabled:opacity-40 flex items-center justify-center space-x-2"
      >
        {isEvaluating ? (
          <>
            <svg viewBox="0 0 24 24" className="w-4 h-4 text-white animate-spin" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M12 2a10 10 0 0 1 10 10"></path>
            </svg>
            <span>Executing Evaluator Pipeline...</span>
          </>
        ) : (
          <>
            <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
            <span>
              {inputMode === "text" ? "Evaluate Speech Transcript" : "Evaluate Spoken Audio Recording"}
            </span>
          </>
        )}
      </button>
    </div>
  );
}
