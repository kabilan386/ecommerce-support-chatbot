"use client";

import { useEffect, useRef, useState } from "react";

interface VoiceButtonProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

export default function VoiceButton({ onTranscript, disabled }: VoiceButtonProps) {
  const [listening, setListening] = useState(false);
  const [supported, setSupported] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      setSupported(true);
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = "en-US";
      rec.onresult = (e: SpeechRecognitionEvent) => {
        const transcript = e.results[0][0].transcript;
        onTranscript(transcript);
        setListening(false);
      };
      rec.onend = () => setListening(false);
      recognitionRef.current = rec;
    }
  }, [onTranscript]);

  const toggle = () => {
    if (!recognitionRef.current) return;
    if (listening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
      setListening(true);
    }
  };

  if (!supported) return null;

  return (
    <button
      onClick={toggle}
      disabled={disabled}
      title={listening ? "Stop recording" : "Start voice input"}
      className={`p-2 rounded-full transition-colors ${
        listening
          ? "bg-red-500 text-white animate-pulse"
          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
      } disabled:opacity-50`}
    >
      {listening ? (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <rect x="5" y="5" width="10" height="10" rx="1" />
        </svg>
      ) : (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 12a4 4 0 004-4V4a4 4 0 00-8 0v4a4 4 0 004 4z" />
          <path d="M5 9a1 1 0 00-2 0 7 7 0 0014 0 1 1 0 00-2 0 5 5 0 01-10 0z" />
          <path d="M10 14v3M7 17h6" strokeWidth="1.5" stroke="currentColor" fill="none" strokeLinecap="round" />
        </svg>
      )}
    </button>
  );
}
