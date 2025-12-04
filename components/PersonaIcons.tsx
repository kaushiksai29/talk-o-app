import React from 'react';

export const StargirlIcon = ({ className }: { className?: string }) => (
    <div className={`relative flex items-center justify-center overflow-hidden rounded-full ${className}`}>
        <img
            src="/stargirl-icon.png"
            alt="Stargirl"
            className="w-full h-full object-cover scale-110"
        />
    </div>
);

export const SageIcon = ({ className }: { className?: string }) => (
    <svg viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
        <path d="M286.5 410H225.5L235 480H277L286.5 410Z" fill="#8D6E63" />
        <path d="M256 40L140 230H210L120 340H190L100 450H412L322 340H392L302 230H372L256 40Z" fill="#7E9E66" stroke="#7E9E66" strokeWidth="10" strokeLinejoin="round" strokeLinecap="round" />
    </svg>
);
