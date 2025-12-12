"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Menu, X, Heart, LogIn, UserPlus, ArrowRight, User, LogOut, LayoutDashboard } from 'lucide-react';
import ThemeToggle from '@/components/ThemeToggle';
import { StargirlIcon, SageIcon } from '@/components/PersonaIcons';
import { useSession, signOut } from "next-auth/react";

export default function LandingPage() {
  const { data: session } = useSession();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [expandedPersona, setExpandedPersona] = useState<string | null>(null);
  const [mobileExpanded, setMobileExpanded] = useState<string | null>(null);

  // Hero scroll animation state
  const [heroOpacity, setHeroOpacity] = useState(1);
  const [heroScale, setHeroScale] = useState(1);

  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      setScrolled(scrollY > 20);

      // Hero animation logic (extended duration)
      const newOpacity = Math.max(0, 1 - scrollY / 3200);
      const newScale = Math.max(0.85, 1 - scrollY / 6400);

      setHeroOpacity(newOpacity);
      setHeroScale(newScale);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  // Desktop Accordion Logic
  const [hoveredPersona, setHoveredPersona] = useState<string | null>(null);
  const [lockedPersona, setLockedPersona] = useState<string | null>(null);

  const handleDesktopEnter = (persona: string) => {
    if (window.innerWidth >= 1024 && !lockedPersona) {
      setHoveredPersona(persona);
    }
  };

  const handleDesktopLeave = () => {
    if (window.innerWidth >= 1024 && !lockedPersona) {
      setHoveredPersona(null);
    }
  };

  const handleDesktopClick = (persona: string) => {
    if (window.innerWidth >= 1024) {
      if (lockedPersona === persona) {
        // Unlock if clicking the same one
        setLockedPersona(null);
        setHoveredPersona(persona); // Keep hovered
      } else {
        setLockedPersona(persona);
        setHoveredPersona(persona);
      }
    }
  };

  // Determine active persona (locked takes precedence over hover)
  const activePersona = lockedPersona || hoveredPersona;

  // Mobile Accordion Logic
  const toggleMobilePersona = (persona: string) => {
    if (mobileExpanded === persona) {
      setMobileExpanded(null);
    } else {
      setMobileExpanded(persona);
    }
  };

  return (
    <div className="min-h-screen font-sans text-coffee-dark dark:text-cream-100 selection:bg-pecan-200 dark:selection:bg-violet-sky-light selection:text-coffee-dark transition-colors duration-500 bg-cream-50 dark:bg-[#0f0e2a]">

      {/* --- Navigation Bar --- */}
      <nav
        className={`fixed w-full z-50 transition-all duration-300 border-b ${scrolled
          ? 'bg-white/90 dark:bg-[#0f172a]/90 backdrop-blur-md shadow-sm border-cream-200 dark:border-white/5 py-3'
          : 'bg-transparent border-transparent py-5'
          }`}
      >
        <div className="container mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={toggleMenu}
              className="md:hidden p-2 hover:bg-cream-100 dark:hover:bg-white/10 rounded-lg transition-colors text-coffee-light dark:text-cream-400"
              aria-label="Open Menu"
            >
              <Menu className="w-6 h-6" />
            </button>

            <div className="text-2xl font-bold tracking-tight flex items-center gap-2 font-serif">
              <div className="flex -space-x-2">
                <div className="w-6 h-6 rounded-full bg-purple-400 opacity-90"></div>
                <div className="w-6 h-6 rounded-full bg-emerald-400 opacity-90"></div>
              </div>
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-emerald-600">Talk-o</span>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-6">
            <Link href="#intro" className="text-sm font-medium text-coffee-light dark:text-cream-300 hover:text-pecan-dark dark:hover:text-violet-sky-light transition-colors">What is Talk-o</Link>
            <Link href="#personas" className="text-sm font-medium text-coffee-light dark:text-cream-300 hover:text-pecan-dark dark:hover:text-violet-sky-light transition-colors">Personas</Link>
            <Link href="#about" className="text-sm font-medium text-coffee-light dark:text-cream-300 hover:text-pecan-dark dark:hover:text-violet-sky-light transition-colors">About</Link>

            <div className="h-4 w-px bg-cream-300 dark:bg-white/10 mx-2"></div>

            <div className="h-4 w-px bg-cream-300 dark:bg-white/10 mx-2"></div>

            <ThemeToggle />

            {session ? (
              <div className="relative">
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center gap-2 px-3 py-2 rounded-full hover:bg-cream-100 dark:hover:bg-white/10 transition-colors"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-emerald-400 p-[2px]">
                    <div className="w-full h-full rounded-full bg-white dark:bg-[#0f172a] flex items-center justify-center overflow-hidden">
                      {session.user?.image ? (
                        <img src={session.user.image} alt="User" className="w-full h-full object-cover" />
                      ) : (
                        <User className="w-4 h-4 text-coffee-light dark:text-cream-400" />
                      )}
                    </div>
                  </div>
                  <span className="text-sm font-medium text-coffee-dark dark:text-cream-200 max-w-[100px] truncate">
                    {session.user?.name || "User"}
                  </span>
                </button>

                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-[#1e1b4b] rounded-2xl shadow-xl border border-cream-200 dark:border-white/10 overflow-hidden py-2 animate-fade-in origin-top-right">
                    <Link href="/dashboard" className="flex items-center gap-3 px-4 py-3 text-sm text-coffee-dark dark:text-cream-200 hover:bg-cream-50 dark:hover:bg-white/5 transition-colors">
                      <LayoutDashboard className="w-4 h-4" /> Dashboard
                    </Link>
                    <button
                      onClick={() => signOut()}
                      className="w-full flex items-center gap-3 px-4 py-3 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10 transition-colors"
                    >
                      <LogOut className="w-4 h-4" /> Log Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <Link href="/login" className="px-4 py-2 text-sm font-medium text-coffee-light dark:text-cream-300 hover:text-pecan-dark dark:hover:text-violet-sky-light transition-colors">
                  Login
                </Link>
                <Link href="/login?mode=register" className="px-5 py-2 text-sm font-medium bg-coffee-dark dark:bg-violet-sky-dark text-white rounded-full hover:bg-coffee/90 dark:hover:bg-violet-sky transition-all shadow hover:shadow-md">
                  Sign Up
                </Link>
              </>
            )}
          </div>

          <div className="md:hidden flex items-center gap-2">
            <ThemeToggle />
          </div>
        </div>
      </nav>

      {/* --- Mobile Menu Panel --- */}
      <div
        className={`fixed inset-0 z-40 bg-coffee-dark/20 dark:bg-black/50 backdrop-blur-sm transition-opacity duration-300 ${isMenuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
        onClick={toggleMenu}
      >
        <div
          className={`absolute top-0 left-0 w-80 h-full bg-white dark:bg-[#0f172a] shadow-2xl transform transition-transform duration-300 ease-out p-6 flex flex-col gap-6 ${isMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between mb-4">
            <span className="text-xl font-bold text-slate-800 dark:text-white font-serif">Talk-o</span>
            <button onClick={toggleMenu} className="p-2 hover:bg-cream-100 dark:hover:bg-white/10 rounded-full">
              <X className="w-6 h-6 text-coffee-light dark:text-cream-400" />
            </button>
          </div>
          <nav className="flex flex-col gap-2">
            <Link href="#intro" onClick={toggleMenu} className="px-4 py-3 text-coffee-dark dark:text-cream-200 hover:bg-cream-50 dark:hover:bg-white/5 rounded-xl transition-colors font-medium">What is Talk-o</Link>
            <Link href="#personas" onClick={toggleMenu} className="px-4 py-3 text-coffee-dark dark:text-cream-200 hover:bg-cream-50 dark:hover:bg-white/5 rounded-xl transition-colors font-medium">Personas</Link>
            {session ? (
              <>
                <Link href="/dashboard" className="flex items-center gap-3 px-4 py-3 text-coffee-dark dark:text-cream-200 hover:bg-cream-50 dark:hover:bg-white/5 rounded-xl transition-colors font-medium">
                  <LayoutDashboard className="w-5 h-5" /> Dashboard
                </Link>
                <button
                  onClick={() => signOut()}
                  className="flex items-center gap-3 px-4 py-3 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10 rounded-xl transition-colors font-medium w-full text-left"
                >
                  <LogOut className="w-5 h-5" /> Log Out
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="flex items-center gap-3 px-4 py-3 text-coffee-dark dark:text-cream-200 hover:bg-cream-50 dark:hover:bg-white/5 rounded-xl transition-colors font-medium">
                  <LogIn className="w-5 h-5" /> Login
                </Link>
                <Link href="/login?mode=register" className="flex items-center gap-3 px-4 py-3 bg-coffee-dark dark:bg-violet-sky-dark text-white hover:bg-coffee/90 dark:hover:bg-violet-sky rounded-xl transition-colors font-medium shadow-sm">
                  <UserPlus className="w-5 h-5" /> Sign Up
                </Link>
              </>
            )}
          </nav>
        </div>
      </div>

      {/* --- Hero Section (Scroll Driven) --- */}
      <section id="hero" className="relative h-[400vh] flex justify-center">
        <div className="sticky top-0 h-screen w-full flex items-center justify-center overflow-hidden">

          {/* Option A: Abstract Flowing Gradient Background - Dark Mode Brightened */}
          <div className="absolute inset-0 -z-10 bg-hero-gradient dark:bg-hero-gradient-dark bg-[length:200%_200%] animate-gradient-shift dark:opacity-100"></div>
          <div className="absolute inset-0 -z-20 bg-cream-50 dark:bg-[#0f0e2a]"></div>

          {/* Floating Orbs (Subtle) */}
          <div className="absolute top-[10%] left-[5%] w-[400px] h-[400px] bg-purple-400/10 rounded-full blur-[100px] animate-gentle-float"></div>
          <div className="absolute bottom-[10%] right-[5%] w-[500px] h-[500px] bg-teal-400/10 rounded-full blur-[100px] animate-gentle-float" style={{ animationDelay: '2s' }}></div>

          {/* Grain Texture Overlay */}
          <div className="absolute inset-0 opacity-[0.05] pointer-events-none" style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E")` }}></div>

          {/* Content */}
          <div
            className="text-center px-6 max-w-5xl z-10 transition-transform duration-100 ease-out"
            style={{
              opacity: heroOpacity,
              transform: `translateY(0) scale(${heroScale})`
            }}
          >
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-extrabold text-coffee-dark dark:text-white leading-[1.1] tracking-tight mb-8 font-serif drop-shadow-sm">
              Silence the chaos. <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-stargirl-primary to-sage-primary">
                Find your flow.
              </span>
            </h1>
            <p className="text-xl md:text-3xl font-light text-coffee-light dark:text-cream-100 max-w-3xl mx-auto leading-relaxed">
              An ADHD companion that meets you exactly where you are.
            </p>

            <button
              onClick={() => document.getElementById('intro')?.scrollIntoView({ behavior: 'smooth' })}
              className="mt-12 animate-bounce text-coffee-light/50 dark:text-cream-200/30 hover:text-coffee-light dark:hover:text-cream-200 transition-colors cursor-pointer"
              aria-label="Scroll to next section"
            >
              <ArrowRight className="w-8 h-8 mx-auto rotate-90" />
            </button>
          </div>
        </div>
      </section>

      {/* --- Intro Section --- */}
      <section id="intro" className="py-32 px-6 max-w-4xl mx-auto relative z-20 bg-cream-50 dark:bg-[#0f0e2a]">
        <h2 className="text-4xl md:text-6xl font-serif text-center mb-16 leading-tight text-coffee-dark dark:text-cream-50">
          You're not broken.<br />
          <span className="text-pecan-dark dark:text-violet-sky-light">You're just wired differently.</span>
        </h2>
        <div className="space-y-8 text-lg md:text-xl font-light leading-relaxed text-coffee-light dark:text-cream-200">
          <p>
            ADHD isn't about lacking focus - it's about having too much of it, scattered everywhere at once. Your brain isn't broken; it's running a different operating system.
          </p>
          <p>
            Talk-o understands that. Two distinct AI companions, each designed for a specific state of mind. Not a one-size-fits-all productivity tool, but two safe spaces tailored to the chaos you're navigating right now.
          </p>
          <p>
            When nighttime anxiety hits and your thoughts won't stop spiraling, you need <Link href="#personas" className="font-bold text-stargirl-primary hover:underline">Stargirl</Link> - gentle, empathetic, someone who won't judge. When daytime overwhelm paralyzes you with a mountain of tasks, you need <Link href="#personas" className="font-bold text-sage-dark hover:underline">Sage</Link> - practical, structured, someone who helps you break it down.
          </p>
        </div>
      </section>

      {/* --- How It Works (Human Version) --- */}
      <section className="py-24 px-6 max-w-5xl mx-auto relative z-20 bg-cream-50 dark:bg-[#0f0e2a]">
        <h2 className="text-4xl md:text-6xl font-serif text-center mb-16 text-coffee-dark dark:text-cream-50">Here's the whole thing.</h2>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white dark:bg-white/5 p-8 rounded-[2rem] border border-cream-200 dark:border-white/10">
            <div className="text-4xl mb-6">🧠</div>
            <h3 className="text-xl font-bold mb-4 text-coffee-dark dark:text-cream-100">1. Pick your brain state</h3>
            <p className="text-coffee-light dark:text-cream-300">Are you spiraling (Stargirl) or paralyzed by tasks (Sage)? Choose the one that matches your current chaos.</p>
          </div>

          <div className="bg-white dark:bg-white/5 p-8 rounded-[2rem] border border-cream-200 dark:border-white/10">
            <div className="text-4xl mb-6">💬</div>
            <h3 className="text-xl font-bold mb-4 text-coffee-dark dark:text-cream-100">2. Just talk</h3>
            <p className="text-coffee-light dark:text-cream-300">No forms, no settings. Just type (or talk) like you would to a friend. They already get it.</p>
          </div>

          <div className="bg-white dark:bg-white/5 p-8 rounded-[2rem] border border-cream-200 dark:border-white/10">
            <div className="text-4xl mb-6">✨</div>
            <h3 className="text-xl font-bold mb-4 text-coffee-dark dark:text-cream-100">3. Feel better</h3>
            <p className="text-coffee-light dark:text-cream-300">Whether it's calming the spiral or breaking down the task, you'll leave feeling lighter. That's it.</p>
          </div>
        </div>
      </section>

      {/* --- The Difference Section (Human Version) --- */}
      <section className="py-32 px-6 max-w-4xl mx-auto relative z-20 bg-cream-50 dark:bg-[#0f0e2a]">
        <h2 className="text-4xl md:text-6xl font-serif text-center mb-16 text-coffee-dark dark:text-cream-50">We get it because we live it.</h2>

        <div className="space-y-8 text-lg md:text-xl font-light leading-relaxed text-coffee-light dark:text-cream-200 text-center max-w-3xl mx-auto">
          <p>
            Talk-o doesn't tell you to "just focus" because that's not how it works. It doesn't suggest you "try waking up earlier" because that's not the problem.
          </p>

          <p>
            It's built by someone who's stared at the wall for 4 hours instead of doing the one thing on the list. Who's cried over feedback that wasn't even that bad. Who's reorganized their entire room at 3am instead of sleeping.
          </p>

          <p className="font-medium text-coffee-dark dark:text-cream-100 text-2xl mt-8">
            That's why it actually helps.
          </p>
        </div>
      </section>

      {/* --- Personas Accordion Section --- */}
      <section id="personas" className="py-32 px-6 max-w-[1400px] mx-auto relative z-20 bg-cream-50 dark:bg-[#0f0e2a]">
        <h2 className="text-4xl md:text-6xl font-serif text-center mb-16 text-coffee-dark dark:text-cream-50">Choose your companion</h2>

        {/* Desktop Accordion (Centered Icons Default) */}
        <div
          className="hidden lg:flex justify-center items-center gap-6 min-h-[550px] transition-all duration-700 w-full px-[40px]"
          onClick={() => { setLockedPersona(null); setHoveredPersona(null); }}
        >

          {/* Stargirl Panel */}
          <div
            className={`relative cursor-pointer transition-all duration-[2000ms] ease-[cubic-bezier(0.2,0.8,0.2,1)] shadow-2xl shadow-stargirl-primary/20 group ${activePersona === 'stargirl'
              ? 'w-[90%] h-[550px] flex-grow rounded-[2.5rem] overflow-auto'
              : activePersona === 'sage'
                ? 'w-[140px] h-[140px] flex-shrink-0 opacity-50 hover:opacity-100 rounded-[2.5rem] overflow-hidden'
                : 'w-[140px] h-[140px] rounded-[2.5rem] overflow-hidden'
              }`}
            onMouseEnter={() => handleDesktopEnter('stargirl')}
            onMouseLeave={handleDesktopLeave}
            onClick={(e) => { e.stopPropagation(); handleDesktopClick('stargirl'); }}
          >
            {/* Background Layers */}
            <div className="absolute inset-0 bg-stargirl-gradient animate-gradient-shift"></div>
            {/* Stars Pattern */}
            <div className="absolute inset-0 opacity-40 animate-twinkle"
              style={{
                backgroundImage: `
                     radial-gradient(2px 2px at 20% 30%, white, transparent),
                     radial-gradient(2px 2px at 60% 70%, white, transparent),
                     radial-gradient(1px 1px at 50% 50%, white, transparent),
                     radial-gradient(2px 2px at 80% 10%, white, transparent),
                     radial-gradient(1px 1px at 10% 60%, white, transparent),
                     radial-gradient(2px 2px at 95% 85%, white, transparent),
                     radial-gradient(1px 1px at 40% 20%, white, transparent),
                     radial-gradient(1px 1px at 70% 40%, white, transparent)
                   `,
                backgroundSize: '250px 250px'
              }}>
            </div>
            {/* Watercolor Overlay */}
            <div className="absolute inset-0 opacity-30"
              style={{
                background: `
                     radial-gradient(ellipse at 30% 40%, rgba(224,195,252,0.4) 0%, transparent 60%),
                     radial-gradient(ellipse at 70% 60%, rgba(142,197,252,0.3) 0%, transparent 55%),
                     radial-gradient(ellipse at 50% 30%, rgba(200,210,252,0.2) 0%, transparent 65%)
                   `
              }}>
            </div>

            {/* Content Container */}
            <div className={`relative h-full flex flex-col justify-between text-white transition-all duration-500 ${activePersona === 'stargirl' ? 'p-8' : 'p-0 items-center justify-center'}`}>

              {/* Icon Only View (Collapsed/Default) */}
              <div className={`absolute inset-0 flex items-center justify-center transition-opacity duration-500 ${activePersona === 'stargirl' ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
                <div className="p-3 bg-white/10 backdrop-blur-md rounded-[2.5rem] border border-white/20 group-hover:scale-110 transition-transform duration-300">
                  <StargirlIcon className="w-14 h-14" />
                </div>
              </div>

              {/* Full Content View (Expanded) */}
              <div className={`${activePersona === 'stargirl' ? 'flex' : 'hidden'} h-full flex-col opacity-0 animate-fade-up`} style={{ animationDelay: '200ms', animationFillMode: 'forwards' }}>
                {/* Header */}
                <div className="flex items-center gap-4 mb-4">
                  <div className="p-3 bg-white/20 backdrop-blur-md rounded-2xl border border-white/20 shadow-lg">
                    <StargirlIcon className="w-10 h-10" />
                  </div>
                  <div>
                    <h3 className="text-3xl lg:text-4xl font-serif mb-1 drop-shadow-md">Stargirl</h3>
                    <p className="text-sm lg:text-base font-light opacity-95 drop-shadow-sm">For when thoughts won't quiet down</p>
                  </div>
                </div>

                {/* Desktop: Horizontal layout (content left, button right) */}
                {/* Mobile: Vertical layout (content top, button bottom) */}
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between flex-grow gap-4">
                  <div className="lg:max-w-[65%]">
                    <p className="text-base lg:text-lg font-light leading-relaxed mb-4 opacity-100 drop-shadow-sm">
                      Gentle support for nighttime spirals, racing thoughts, and when you need someone who truly listens.
                    </p>
                    <div className="space-y-3">
                      <div className="p-3 bg-white/15 backdrop-blur-xl rounded-xl border border-white/20 shadow-lg">
                        <p className="text-sm lg:text-base italic font-light">"I hear you, and that sounds really tough. 🌙 Your feelings are completely valid."</p>
                      </div>
                      <div className="p-3 bg-white/15 backdrop-blur-xl rounded-xl border border-white/20 shadow-lg">
                        <p className="text-sm lg:text-base italic font-light">"Let's ground together - can you feel your feet on the floor?"</p>
                      </div>
                    </div>
                  </div>
                  <div className="lg:flex-shrink-0">
                    <Link href="/chat?model=stargirl" className="inline-flex items-center gap-2 px-6 py-3 bg-white text-stargirl-dark rounded-full font-bold text-sm lg:text-base hover:scale-105 transition-transform shadow-xl">
                      Chat with Stargirl <ArrowRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Sage Panel */}
          <div
            className={`relative cursor-pointer transition-all duration-[2000ms] ease-[cubic-bezier(0.2,0.8,0.2,1)] shadow-2xl shadow-sage-primary/20 group ${activePersona === 'sage'
              ? 'w-[90%] h-[550px] flex-grow rounded-[2.5rem] overflow-auto'
              : activePersona === 'stargirl'
                ? 'w-[140px] h-[140px] flex-shrink-0 opacity-50 hover:opacity-100 rounded-[2.5rem] overflow-hidden'
                : 'w-[140px] h-[140px] rounded-[2.5rem] overflow-hidden'
              }`}
            onMouseEnter={() => handleDesktopEnter('sage')}
            onMouseLeave={handleDesktopLeave}
            onClick={(e) => { e.stopPropagation(); handleDesktopClick('sage'); }}
          >
            {/* Background Layers */}
            <div className="absolute inset-0 bg-sage-gradient animate-gradient-shift"></div>
            {/* Grid Pattern */}
            <div className="absolute inset-0 opacity-20"
              style={{
                backgroundImage: `
                     linear-gradient(rgba(255,255,255,0.5) 1.5px, transparent 1.5px),
                     linear-gradient(90deg, rgba(255,255,255,0.5) 1.5px, transparent 1.5px)
                   `,
                backgroundSize: '35px 35px'
              }}>
            </div>
            {/* Nature Gradient Overlay */}
            <div className="absolute inset-0 opacity-30"
              style={{
                background: `
                     radial-gradient(ellipse at 40% 50%, rgba(212,252,121,0.4) 0%, transparent 65%),
                     radial-gradient(ellipse at 70% 40%, rgba(150,230,161,0.3) 0%, transparent 60%),
                     radial-gradient(ellipse at 30% 70%, rgba(181,232,157,0.25) 0%, transparent 58%)
                   `
              }}>
            </div>

            {/* Content Container */}
            <div className={`relative h-full flex flex-col justify-between text-coffee-dark transition-all duration-500 ${activePersona === 'sage' ? 'p-8' : 'p-0 items-center justify-center'}`}>

              {/* Icon Only View (Collapsed/Default) */}
              <div className={`absolute inset-0 flex items-center justify-center transition-opacity duration-500 ${activePersona === 'sage' ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
                <div className="p-3 bg-white/30 backdrop-blur-md rounded-[2.5rem] border border-white/20 group-hover:scale-110 transition-transform duration-300">
                  <SageIcon className="w-14 h-14" />
                </div>
              </div>

              {/* Full Content View (Expanded) */}
              <div className={`${activePersona === 'sage' ? 'flex' : 'hidden'} h-full flex-col opacity-0 animate-fade-up`} style={{ animationDelay: '200ms', animationFillMode: 'forwards' }}>
                {/* Header */}
                <div className="flex items-center gap-4 mb-4">
                  <div className="p-3 bg-white/40 backdrop-blur-md rounded-2xl border border-white/20 shadow-lg">
                    <SageIcon className="w-10 h-10" />
                  </div>
                  <div>
                    <h3 className="text-3xl lg:text-4xl font-serif mb-1 font-medium">Sage</h3>
                    <p className="text-sm lg:text-base font-medium opacity-85">For when everything feels overwhelming</p>
                  </div>
                </div>

                {/* Desktop: Horizontal layout (content left, button right) */}
                {/* Mobile: Vertical layout (content top, button bottom) */}
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between flex-grow gap-4">
                  <div className="lg:max-w-[65%]">
                    <p className="text-base lg:text-lg font-medium leading-relaxed mb-4 opacity-90">
                      Practical structure for task paralysis and breaking down the impossible into doable steps.
                    </p>
                    <div className="space-y-3">
                      <div className="p-3 bg-white/30 backdrop-blur-xl rounded-xl border border-white/30 shadow-lg">
                        <p className="text-sm lg:text-base italic font-medium">"Let's make this smaller - what's ONE tiny thing you could do in the next 5 minutes?"</p>
                      </div>
                      <div className="p-3 bg-white/30 backdrop-blur-xl rounded-xl border border-white/30 shadow-lg">
                        <p className="text-sm lg:text-base italic font-medium">"What must happen today vs. what can wait? Let's prioritize together."</p>
                      </div>
                    </div>
                  </div>
                  <div className="lg:flex-shrink-0">
                    <Link href="/chat?model=sage" className="inline-flex items-center gap-2 px-6 py-3 bg-white text-sage-dark rounded-full font-bold text-sm lg:text-base hover:scale-105 transition-transform shadow-xl">
                      Chat with Sage <ArrowRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* Mobile Accordion (Stacked with Reordering) */}
        <div className="lg:hidden flex flex-col gap-6">

          {/* Stargirl Mobile */}
          <div
            className={`rounded-[3rem] overflow-hidden cursor-pointer transition-all duration-[600ms] ease-[cubic-bezier(0.4,0,0.2,1)] shadow-xl shadow-stargirl-primary/20 relative ${mobileExpanded === 'stargirl' ? 'order-last scale-[1.02]' : 'order-first scale-100'
              }`}
            onClick={() => toggleMobilePersona('stargirl')}
          >
            <div className="absolute inset-0 bg-gradient-to-br from-stargirl-light to-stargirl-dark"></div>
            <div className="absolute inset-0 opacity-30" style={{ backgroundImage: 'radial-gradient(white 2px, transparent 2px)', backgroundSize: '40px 40px' }}></div>

            <div className="relative p-8 text-white">
              <div className="flex items-center gap-4 mb-6">
                <div className="p-4 bg-white/10 backdrop-blur-md rounded-2xl">
                  <StargirlIcon className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-3xl font-serif">Stargirl</h3>
                  <p className="text-sm opacity-90 font-light">For when thoughts won't quiet down</p>
                </div>
              </div>

              {mobileExpanded === 'stargirl' && (
                <div className="animate-fade-up" style={{ animationDelay: '300ms' }}>
                  <p className="text-lg font-light mb-6 opacity-95">Gentle support for nighttime spirals and racing thoughts.</p>
                  <div className="p-6 bg-white/15 backdrop-blur-md rounded-3xl mb-6">
                    <p className="italic font-light">"I hear you. Your feelings are valid. 🌙"</p>
                  </div>
                  <Link href="/chat?model=stargirl" className="block w-full text-center py-4 bg-white text-stargirl-dark rounded-full font-bold shadow-lg">
                    Chat with Stargirl
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Sage Mobile */}
          <div
            className={`rounded-[3rem] overflow-hidden cursor-pointer transition-all duration-[600ms] ease-[cubic-bezier(0.4,0,0.2,1)] shadow-xl shadow-sage-primary/20 relative ${mobileExpanded === 'sage' ? 'order-last scale-[1.02]' : 'order-first scale-100'
              }`}
            onClick={() => toggleMobilePersona('sage')}
          >
            <div className="absolute inset-0 bg-gradient-to-br from-sage-light to-sage-secondary"></div>
            <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,0.5) 1.5px, transparent 1.5px), linear-gradient(90deg, rgba(255,255,255,0.5) 1.5px, transparent 1.5px)', backgroundSize: '35px 35px' }}></div>

            <div className="relative p-8 text-coffee-dark">
              <div className="flex items-center gap-4 mb-6">
                <div className="p-4 bg-white/30 backdrop-blur-md rounded-2xl">
                  <SageIcon className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-3xl font-serif">Sage</h3>
                  <p className="text-sm opacity-85 font-light">For when everything feels overwhelming</p>
                </div>
              </div>

              {mobileExpanded === 'sage' && (
                <div className="animate-fade-up" style={{ animationDelay: '300ms' }}>
                  <p className="text-lg font-light mb-6 opacity-90">Practical structure for task paralysis and breaking things down.</p>
                  <div className="p-6 bg-white/30 backdrop-blur-md rounded-3xl mb-6">
                    <p className="italic font-light">"Let's make this smaller - one tiny thing at a time."</p>
                  </div>
                  <Link href="/chat?model=sage" className="block w-full text-center py-4 bg-white text-sage-dark rounded-full font-bold shadow-lg">
                    Chat with Sage
                  </Link>
                </div>
              )}
            </div>
          </div>

        </div>
      </section>

      {/* --- You'll know which one you need (Human Version) --- */}
      <section className="py-32 px-6 max-w-6xl mx-auto relative z-20 bg-cream-50 dark:bg-[#0f0e2a]">
        <h2 className="text-4xl md:text-6xl font-serif text-center mb-16 text-coffee-dark dark:text-cream-50">You'll know which one you need.</h2>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Stargirl Scenario */}
          <div className="group relative overflow-hidden rounded-[3rem] bg-stargirl-section border border-stargirl-light/30 dark:border-stargirl-primary/20 p-10 transition-all hover:-translate-y-2 hover:shadow-2xl hover:shadow-stargirl-primary/10">
            <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
              <StargirlIcon className="w-48 h-48 text-stargirl-primary" />
            </div>

            <div className="relative z-10">
              <p className="text-xl font-light leading-relaxed text-coffee-dark dark:text-cream-100 mb-8">
                It's late. You're spiraling about something someone said three days ago. You know it's probably nothing but your brain won't let it go.
              </p>
              <p className="text-2xl font-serif text-stargirl-primary font-bold">That's a Stargirl moment.</p>
            </div>
          </div>

          {/* Sage Scenario */}
          <div className="group relative overflow-hidden rounded-[3rem] bg-sage-section border border-sage-light/30 dark:border-sage-primary/20 p-10 transition-all hover:-translate-y-2 hover:shadow-2xl hover:shadow-sage-primary/10">
            <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
              <SageIcon className="w-48 h-48 text-sage-primary" />
            </div>

            <div className="relative z-10">
              <p className="text-xl font-light leading-relaxed text-coffee-dark dark:text-cream-100 mb-8">
                You're staring at your to-do list. Everything feels urgent and impossible. You don't know where to start so you start nothing.
              </p>
              <p className="text-2xl font-serif text-sage-primary font-bold">That's a Sage moment.</p>
            </div>
          </div>
        </div>
      </section>

      {/* --- Conversation Preview Section (Human Version) --- */}
      <section className="py-32 px-6 max-w-4xl mx-auto relative z-20 bg-cream-50 dark:bg-[#0f0e2a]">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-6xl font-serif text-coffee-dark dark:text-cream-50 mb-4">This is what it's like.</h2>
        </div>

        <div className="bg-white dark:bg-[#1e1b4b] rounded-[2.5rem] shadow-2xl border border-cream-200 dark:border-white/10 overflow-hidden">
          {/* Chat Header */}
          <div className="bg-stargirl-light/30 dark:bg-stargirl-dark/30 p-6 flex items-center gap-4 border-b border-stargirl-light/20">
            <div className="w-12 h-12 bg-stargirl-primary rounded-full flex items-center justify-center text-white">
              <StargirlIcon className="w-7 h-7" />
            </div>
            <div>
              <h3 className="font-bold text-coffee-dark dark:text-cream-100">Stargirl</h3>
              <p className="text-sm text-stargirl-primary dark:text-stargirl-light">Always here for you</p>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="p-8 space-y-8 bg-cream-50/50 dark:bg-[#0f0e2a]/50">
            {/* User Message */}
            <div className="flex justify-end">
              <div className="bg-stargirl-primary text-white px-6 py-4 rounded-2xl rounded-tr-sm max-w-[80%] shadow-md">
                <p className="text-lg">I stared at the wall for 4 hours instead of working. I'm so useless.</p>
              </div>
            </div>

            {/* Stargirl Message */}
            <div className="flex justify-start">
              <div className="bg-white dark:bg-[#1e1b4b] text-coffee-dark dark:text-cream-100 px-6 py-4 rounded-2xl rounded-tl-sm max-w-[85%] shadow-md border border-cream-200 dark:border-white/10">
                <p className="text-lg leading-relaxed">
                  Dude I feel that so hard. The wall staring thing is real and it's brutal. <span className="font-bold text-stargirl-primary">You're not useless</span> - your brain just got stuck in that paralysis loop. Were you trying to start something specific or just... frozen?
                </p>
              </div>
            </div>

            {/* User Message */}
            <div className="flex justify-end">
              <div className="bg-stargirl-primary text-white px-6 py-4 rounded-2xl rounded-tr-sm max-w-[80%] shadow-md">
                <p className="text-lg">Frozen. I couldn't even pick what to start with.</p>
              </div>
            </div>

            {/* Stargirl Message */}
            <div className="flex justify-start">
              <div className="bg-white dark:bg-[#1e1b4b] text-coffee-dark dark:text-cream-100 px-6 py-4 rounded-2xl rounded-tl-sm max-w-[85%] shadow-md border border-cream-200 dark:border-white/10">
                <p className="text-lg leading-relaxed">
                  Ugh, the "too many things so I'll do none of them" trap. That's not laziness, that's your brain short-circuiting from overwhelm. <br /><br />
                  What's <span className="font-bold text-stargirl-primary">ONE tiny thing</span> on that list? Like, stupidly small.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- Gentle CTA (Human Version) --- */}
      <section className="py-24 px-6 text-center relative z-20 bg-cream-50 dark:bg-[#0f0e2a]">
        <h2 className="text-3xl md:text-5xl font-serif text-coffee-dark dark:text-cream-50 mb-6">If you want to try it, it's free.</h2>
        <p className="text-xl font-light text-coffee-light dark:text-cream-200 mb-10 max-w-2xl mx-auto">
          No credit card, no trial period that secretly charges you. Just see if it helps.
        </p>
        <Link href={session ? "/dashboard" : "/login"} className="inline-flex items-center gap-3 px-8 py-4 bg-coffee-dark dark:bg-violet-sky-dark text-white rounded-full font-bold text-lg hover:scale-105 transition-transform shadow-xl">
          Start Talking <ArrowRight className="w-5 h-5" />
        </Link>
      </section>

      {/* --- About Section (Human Version - No Title) --- */}
      {/* --- Meet the Maker (Simplified) --- */}
      <section id="about" className="py-32 px-6 max-w-4xl mx-auto relative z-20 bg-cream-50 dark:bg-[#0f0e2a]">
        <h2 className="text-4xl md:text-6xl font-serif text-center mb-16 text-coffee-dark dark:text-cream-50">Meet the maker</h2>

        <div className="bg-white dark:bg-white/5 rounded-[3rem] p-8 md:p-12 shadow-sm border border-cream-200 dark:border-white/10 text-center">

          {/* Bio Content */}
          <div className="space-y-6 text-lg font-light leading-relaxed text-coffee-light dark:text-cream-200 max-w-3xl mx-auto">
            <p>
              I built Talk-o because I needed it. As someone with ADHD navigating life, I was tired of productivity apps designed by people who've never experienced executive dysfunction.
            </p>
            <p>
              This isn't a corporate product. It's a passion project born from 2 AM spirals and countless days frozen by overwhelm. If Talk-o helps you even a little, that means everything.
            </p>
          </div>

          {/* Support Button */}
          <div className="mt-10 flex justify-center">
            <a href="https://buymeacoffee.com/kaushiksaikadali" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-3 px-6 py-3 bg-cream-100 dark:bg-white/10 hover:bg-cream-200 dark:hover:bg-white/20 rounded-xl transition-colors text-coffee-dark dark:text-cream-100 font-medium">
              <Heart className="w-5 h-5 text-red-400 fill-red-400" />
              Support this project
            </a>
          </div>
        </div>
      </section>

      {/* --- Footer --- */}
      <footer className="py-12 px-6 border-t border-cream-200 dark:border-white/10 text-center bg-cream-50 dark:bg-[#0f172a] relative z-20">
        <p className="text-sm text-coffee-light dark:text-cream-400 font-light">
          Made with care for neurodivergent minds • © 2025 Talk-o
        </p>
      </footer>

    </div>
  );
}
