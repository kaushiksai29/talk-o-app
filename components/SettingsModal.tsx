"use client";

import React, { useState, useEffect } from 'react';
import { X, Save, Trash2, AlertTriangle } from 'lucide-react';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase Client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
const supabase = createClient(supabaseUrl, supabaseKey);

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    userId?: string;
}

export default function SettingsModal({ isOpen, onClose, userId }: SettingsModalProps) {
    const [activeTab, setActiveTab] = useState<'profile' | 'account' | 'data'>('profile');
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
    const [messageCount, setMessageCount] = useState(0);
    const [dataProcessed, setDataProcessed] = useState(0);
    const [realUserId, setRealUserId] = useState<string | undefined>(undefined);

    useEffect(() => {
        const resolveUser = async () => {
            console.log("SettingsModal: Resolving user for:", userId);
            if (!userId) return;

            if (userId.includes('@')) {
                // It's an email, fetch UUID
                const { data, error } = await supabase
                    .from('profiles')
                    .select('id')
                    .eq('email', userId)
                    .single();

                if (error) console.error("SettingsModal: Error resolving email:", error);
                if (data) {
                    console.log("SettingsModal: Resolved email to ID:", data.id);
                    setRealUserId(data.id);
                }
            } else {
                console.log("SettingsModal: Using provided ID:", userId);
                setRealUserId(userId);
            }
        };
        resolveUser();
    }, [userId]);

    useEffect(() => {
        if (isOpen && realUserId) {
            fetchProfile();
            fetchUsage();
        }
    }, [isOpen, realUserId]);

    const fetchProfile = async () => {
        if (!realUserId) return;
        const { data, error } = await supabase
            .from('profiles')
            .select('first_name, last_name')
            .eq('id', realUserId)
            .single();

        if (data) {
            setFirstName(data.first_name || "");
            setLastName(data.last_name || "");
        }
    };

    const fetchUsage = async () => {
        if (!realUserId) return;
        const { count } = await supabase
            .from('chat_history')
            .select('*', { count: 'exact', head: true })
            .eq('user_id', realUserId);

        const countVal = count || 0;
        setMessageCount(countVal);
        // Estimate data processed: avg 150 chars per message * count
        setDataProcessed(countVal * 150);
    };

    const handleUpdateProfile = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setMessage(null);

        try {
            const { error } = await supabase
                .from('profiles')
                .update({ first_name: firstName, last_name: lastName })
                .eq('id', realUserId);

            if (error) throw error;
            setMessage({ type: 'success', text: "Profile updated successfully." });
        } catch (error: any) {
            setMessage({ type: 'error', text: error.message });
        } finally {
            setIsLoading(false);
        }
    };

    const handleUpdatePassword = async (e: React.FormEvent) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            setMessage({ type: 'error', text: "Passwords do not match." });
            return;
        }

        setIsLoading(true);
        setMessage(null);

        try {
            const { error } = await supabase.auth.updateUser({ password: password });
            if (error) throw error;
            setMessage({ type: 'success', text: "Password updated successfully." });
            setPassword("");
            setConfirmPassword("");
        } catch (error: any) {
            setMessage({ type: 'error', text: error.message });
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteHistory = async () => {
        if (!confirm("Are you sure you want to delete all chat history? This cannot be undone.")) return;

        setIsLoading(true);
        setMessage(null);

        try {
            const { error } = await supabase
                .from('chat_history')
                .delete()
                .eq('user_id', realUserId);

            if (error) throw error;
            setMessage({ type: 'success', text: "Chat history deleted." });
            fetchUsage();
        } catch (error: any) {
            setMessage({ type: 'error', text: error.message });
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fade-in">
            <div className="bg-white dark:bg-[#1e1b4b] w-full max-w-2xl rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
                {/* Header */}
                <div className="p-6 border-b border-cream-200 dark:border-white/10 flex justify-between items-center bg-cream-50 dark:bg-[#0f172a]">
                    <h2 className="font-serif text-2xl font-bold text-coffee-dark dark:text-cream-50">Settings</h2>
                    <button onClick={onClose} className="p-2 hover:bg-cream-200 dark:hover:bg-white/10 rounded-full transition-colors text-coffee-light dark:text-cream-400">
                        <X size={24} />
                    </button>
                </div>

                <div className="flex flex-1 overflow-hidden">
                    {/* Sidebar Tabs */}
                    <div className="w-48 bg-cream-50/50 dark:bg-[#0f172a]/50 border-r border-cream-200 dark:border-white/10 p-4 space-y-2">
                        <button
                            onClick={() => setActiveTab('profile')}
                            className={`w-full text-left px-4 py-3 rounded-xl font-medium transition-colors ${activeTab === 'profile'
                                ? 'bg-white dark:bg-white/10 text-coffee-dark dark:text-cream-50 shadow-sm'
                                : 'text-coffee-light dark:text-cream-400 hover:bg-cream-100 dark:hover:bg-white/5'}`}
                        >
                            Profile
                        </button>
                        <button
                            onClick={() => setActiveTab('account')}
                            className={`w-full text-left px-4 py-3 rounded-xl font-medium transition-colors ${activeTab === 'account'
                                ? 'bg-white dark:bg-white/10 text-coffee-dark dark:text-cream-50 shadow-sm'
                                : 'text-coffee-light dark:text-cream-400 hover:bg-cream-100 dark:hover:bg-white/5'}`}
                        >
                            Account
                        </button>
                        <button
                            onClick={() => setActiveTab('data')}
                            className={`w-full text-left px-4 py-3 rounded-xl font-medium transition-colors ${activeTab === 'data'
                                ? 'bg-white dark:bg-white/10 text-coffee-dark dark:text-cream-50 shadow-sm'
                                : 'text-coffee-light dark:text-cream-400 hover:bg-cream-100 dark:hover:bg-white/5'}`}
                        >
                            Data & Usage
                        </button>
                    </div>

                    {/* Content */}
                    <div className="flex-1 p-8 overflow-y-auto bg-white dark:bg-[#1e1b4b]">
                        {message && (
                            <div className={`mb-6 p-4 rounded-xl flex items-center gap-3 ${message.type === 'success'
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-300 dark:border-emerald-900/50'
                                : 'bg-red-50 text-red-700 border border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-900/50'}`}>
                                {message.type === 'error' && <AlertTriangle size={20} />}
                                {message.text}
                            </div>
                        )}

                        {activeTab === 'profile' && (
                            <form onSubmit={handleUpdateProfile} className="space-y-6">
                                <div>
                                    <h3 className="text-lg font-bold text-coffee-dark dark:text-cream-50 mb-4">Personal Information</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-coffee-light dark:text-cream-400">First Name</label>
                                            <input
                                                type="text"
                                                value={firstName}
                                                onChange={(e) => setFirstName(e.target.value)}
                                                className="w-full px-4 py-3 rounded-xl bg-cream-50 dark:bg-white/5 border border-cream-200 dark:border-white/10 text-coffee-dark dark:text-cream-100 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-coffee-light dark:text-cream-400">Last Name</label>
                                            <input
                                                type="text"
                                                value={lastName}
                                                onChange={(e) => setLastName(e.target.value)}
                                                className="w-full px-4 py-3 rounded-xl bg-cream-50 dark:bg-white/5 border border-cream-200 dark:border-white/10 text-coffee-dark dark:text-cream-100 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                                            />
                                        </div>
                                    </div>
                                </div>
                                <button
                                    type="submit"
                                    disabled={isLoading}
                                    className="flex items-center gap-2 px-6 py-3 bg-coffee-dark dark:bg-violet-sky text-white rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50"
                                >
                                    <Save size={18} />
                                    Save Changes
                                </button>
                            </form>
                        )}

                        {activeTab === 'account' && (
                            <form onSubmit={handleUpdatePassword} className="space-y-6">
                                <div>
                                    <h3 className="text-lg font-bold text-coffee-dark dark:text-cream-50 mb-4">Change Password</h3>
                                    <div className="space-y-4">
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-coffee-light dark:text-cream-400">New Password</label>
                                            <input
                                                type="password"
                                                value={password}
                                                onChange={(e) => setPassword(e.target.value)}
                                                className="w-full px-4 py-3 rounded-xl bg-cream-50 dark:bg-white/5 border border-cream-200 dark:border-white/10 text-coffee-dark dark:text-cream-100 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-coffee-light dark:text-cream-400">Confirm Password</label>
                                            <input
                                                type="password"
                                                value={confirmPassword}
                                                onChange={(e) => setConfirmPassword(e.target.value)}
                                                className="w-full px-4 py-3 rounded-xl bg-cream-50 dark:bg-white/5 border border-cream-200 dark:border-white/10 text-coffee-dark dark:text-cream-100 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                                            />
                                        </div>
                                    </div>
                                </div>
                                <button
                                    type="submit"
                                    disabled={isLoading || !password}
                                    className="flex items-center gap-2 px-6 py-3 bg-coffee-dark dark:bg-violet-sky text-white rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50"
                                >
                                    <Save size={18} />
                                    Update Password
                                </button>
                            </form>
                        )}

                        {activeTab === 'data' && (
                            <div className="space-y-8">
                                <div>
                                    <h3 className="text-lg font-bold text-coffee-dark dark:text-cream-50 mb-4">Usage Statistics</h3>
                                    <div className="bg-cream-50 dark:bg-white/5 p-6 rounded-2xl border border-cream-200 dark:border-white/10">
                                        <div className="text-sm text-coffee-light dark:text-cream-400 mb-1">Total Messages Sent</div>
                                        <div className="text-3xl font-bold text-coffee-dark dark:text-cream-50">{messageCount}</div>
                                    </div>
                                    <div className="mt-4 bg-cream-50 dark:bg-white/5 p-6 rounded-2xl border border-cream-200 dark:border-white/10">
                                        <div className="text-sm text-coffee-light dark:text-cream-400 mb-1">Data Processed (Est.)</div>
                                        <div className="text-3xl font-bold text-coffee-dark dark:text-cream-50">{(dataProcessed / 1024).toFixed(2)} KB</div>
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-lg font-bold text-red-600 dark:text-red-400 mb-4">Danger Zone</h3>
                                    <div className="bg-red-50 dark:bg-red-900/10 p-6 rounded-2xl border border-red-200 dark:border-red-900/30 flex items-center justify-between">
                                        <div>
                                            <h4 className="font-bold text-red-700 dark:text-red-300">Delete Chat History</h4>
                                            <p className="text-sm text-red-600/80 dark:text-red-400/80">Permanently remove all your conversations.</p>
                                        </div>
                                        <button
                                            onClick={handleDeleteHistory}
                                            disabled={isLoading}
                                            className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-red-900/20 border border-red-200 dark:border-red-900/50 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
                                        >
                                            <Trash2 size={18} />
                                            Delete All
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
