"use client";

import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Props {
    text: string;
    streaming?: boolean;
}

export default function TypingMessage({ text, streaming }: Props) {
    const [displayedText, setDisplayedText] = useState("");
    const [isTyping, setIsTyping] = useState(true);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Reset when text changes significantly (new message)
    // But for streaming, we just want to append
    useEffect(() => {
        if (!streaming) {
            // If not streaming (e.g. history), show full text immediately
            setDisplayedText(text);
            setIsTyping(false);
            return;
        }

        // If streaming, we might need to catch up if we re-rendered
        // But simpler logic: just sync displayedText to text length gradually
    }, [streaming]);

    useEffect(() => {
        if (!streaming && displayedText === text) return;

        let currentIndex = displayedText.length;
        if (currentIndex >= text.length) {
            if (!streaming) setIsTyping(false);
            return;
        }

        setIsTyping(true);

        const interval = setInterval(() => {
            if (currentIndex < text.length) {
                setDisplayedText(text.slice(0, currentIndex + 1));
                currentIndex++;

                // Auto-scroll to bottom of this element
                if (scrollRef.current) {
                    scrollRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
                }
            } else {
                clearInterval(interval);
                if (!streaming) setIsTyping(false);
            }
        }, 15); // Typing speed (ms per char)

        return () => clearInterval(interval);
    }, [text, streaming]); // Re-run when text updates (stream chunks)

    return (
        <div className="relative leading-relaxed break-words">
            <div className="prose dark:prose-invert max-w-none prose-p:my-2 prose-ul:my-2 prose-li:my-0.5">
                <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                        // Override some elements if needed for custom styling
                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                        ul: ({ node, ...props }) => <ul className="list-disc pl-4 mb-2 space-y-1" {...props} />,
                        ol: ({ node, ...props }) => <ol className="list-decimal pl-4 mb-2 space-y-1" {...props} />,
                        li: ({ node, ...props }) => <li className="pl-1" {...props} />,
                        strong: ({ node, ...props }) => <strong className="font-bold text-current" {...props} />,
                    }}
                >
                    {displayedText}
                </ReactMarkdown>
            </div>

            <div ref={scrollRef} />
        </div>
    );
}
