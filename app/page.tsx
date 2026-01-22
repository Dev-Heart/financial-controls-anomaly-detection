"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Papa from "papaparse";
import {
  Upload,
  FileText,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Activity,
  ShieldAlert,
  Search
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Types
interface Transaction {
  date: string;
  amount: string | number;
  vendor: string;
  [key: string]: any;
}

interface AnalysisResult {
  summary: {
    total_transactions: number;
    duplicates: number;
    unusual_timing: number;
    round_numbers: number;
    threshold_flags: number;
  };
  details: {
    duplicates: any[];
    unusual_timing: any[];
    round_numbers: any[];
    threshold_flags: any[];
    benford: any[];
    fuzzy_duplicates: any[];
  };
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'forensic'>('overview');

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      setResults(null);
      setError(null);
    }
  };

  const parseAndAnalyze = () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async (parseResults) => {
        try {
          const data = parseResults.data as Transaction[];

          // Send to API
          const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
          });

          if (!response.ok) {
            throw new Error('Analysis failed');
          }

          const resultData = await response.json();
          if (resultData.error) throw new Error(resultData.error);

          setResults(resultData);
        } catch (err: any) {
          setError(err.message || 'An error occurred during analysis');
        } finally {
          setLoading(false);
        }
      },
      error: (err) => {
        setError("Failed to parse CSV file: " + err.message);
        setLoading(false);
      }
    });
  };

  const loadSampleData = async () => {
    setLoading(true);
    try {
      // Create a dummy file object or just fetch the sample csv content if available
      // For now, we'll manually define some sample data to simulate the flow
      // or fetch from an endpoint. Since we don't have a GET endpoint for sample,
      // let's construct it manually to test the UI.
      const sampleData = [
        { date: "2024-01-03", amount: 15000, vendor: "ABC Supplies", description: "Dup check" },
        { date: "2024-01-03", amount: 15000, vendor: "ABC Supplies", description: "Dup check" },
        { date: "2024-01-07", amount: 4500, vendor: "CloudSoft", description: "Sunday transaction" },
        { date: "2024-01-05", amount: 10000, vendor: "Consulting", description: "Round number" },
        { date: "2024-01-06", amount: 9999, vendor: "Consulting", description: "Threshold avoidance" },
      ];

      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sampleData),
      });

      const resultData = await response.json();
      setResults(resultData);
    } catch (err) {
      setError("Failed to load sample data.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-200 font-sans selection:bg-emerald-500/30">
      {/* Header */}
      <header className="border-b border-neutral-800 bg-neutral-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-emerald-500/10 p-2 rounded-lg">
              <ShieldAlert className="w-6 h-6 text-emerald-500" />
            </div>
            <span className="font-bold text-lg tracking-tight text-white">Validation<span className="text-emerald-500">IQ</span></span>
          </div>
          <div className="flex items-center gap-4">
            <a href="https://github.com/Dev-Heart" target="_blank" className="text-sm text-neutral-400 hover:text-white transition-colors">By Divine Heart</a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">

        {/* Hero Section */}
        <div className="flex flex-col items-center text-center mb-16 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium"
          >
            <Activity className="w-4 h-4" />
            <span>AI-Powered Financial Forensics</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-5xl md:text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-neutral-500 tracking-tight max-w-4xl"
          >
            Detect Financial Anomalies before they become Audits.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-lg text-neutral-400 max-w-2xl"
          >
            Pattern recognition for finding duplicate payments, round-number biases, and threshold avoidance in seconds.
          </motion.p>
        </div>

        {/* Upload Section */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="max-w-2xl mx-auto mb-20"
        >
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500 to-indigo-500 rounded-2xl opacity-20 group-hover:opacity-40 transition-opacity blur-xl"></div>
            <div className="relative bg-neutral-900 border border-neutral-800 rounded-2xl p-8 shadow-2xl">
              {!results ? (
                <div className="flex flex-col items-center justify-center space-y-6 border-2 border-dashed border-neutral-700 rounded-xl p-10 hover:border-emerald-500/50 hover:bg-neutral-800/50 transition-all">
                  <div className="bg-neutral-800 p-4 rounded-full">
                    <Upload className="w-8 h-8 text-neutral-400" />
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-medium text-white">Upload Transaction CSV</p>
                    <p className="text-sm text-neutral-400 mt-1">Drag and drop or click to browse</p>
                  </div>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  {file && (
                    <div className="absolute bottom-4 left-0 right-0 flex justify-center">
                      <span className="flex items-center gap-2 px-3 py-1 bg-neutral-800 rounded-full text-xs text-neutral-300 border border-neutral-700">
                        <FileText className="w-3 h-3" />
                        {file.name}
                      </span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-10 space-y-4">
                  <div className="bg-emerald-500/20 p-4 rounded-full">
                    <CheckCircle className="w-10 h-10 text-emerald-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-white">Analysis Complete</h3>
                  <button
                    onClick={() => setResults(null)}
                    className="text-sm text-neutral-400 hover:text-white border-b border-transparent hover:border-white transition-colors"
                  >
                    Analyze another file
                  </button>
                </div>
              )}

              <div className="mt-6 flex gap-3">
                <button
                  onClick={parseAndAnalyze}
                  disabled={!file || loading}
                  className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-3 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4" />
                      Run Analysis
                    </>
                  )}
                </button>
                <button
                  onClick={loadSampleData}
                  disabled={loading}
                  className="px-4 py-3 bg-neutral-800 hover:bg-neutral-700 text-neutral-300 rounded-lg font-medium transition-colors"
                >
                  Try Sample
                </button>
              </div>

              {error && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-2 text-red-400 text-sm">
                  <AlertTriangle className="w-4 h-4" />
                  {error}
                </div>
              )}
            </div>
          </div>
        </motion.div>

        {/* Results Dashboard */}
        <AnimatePresence>
          {results && (
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="space-y-8"
            >
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                  label="Duplicate Payments"
                  value={results.summary.duplicates}
                  icon={<FileText className="w-5 h-5 text-purple-400" />}
                  color="purple"
                />
                <StatCard
                  label="Unusual Timing"
                  value={results.summary.unusual_timing}
                  icon={<Activity className="w-5 h-5 text-orange-400" />}
                  color="orange"
                />
                <StatCard
                  label="Round Numbers"
                  value={results.summary.round_numbers}
                  icon={<BarChart3 className="w-5 h-5 text-blue-400" />}
                  color="blue"
                />
                <StatCard
                  label="Threshold Avoidance"
                  value={results.summary.threshold_flags}
                  icon={<ShieldAlert className="w-5 h-5 text-red-400" />}
                  color="red"
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Chart */}
                <div className="lg:col-span-2 bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-6">Anomaly Distribution</h3>
                  <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={[
                          { name: 'Duplicates', value: results.summary.duplicates, color: '#a855f7' },
                          { name: 'Timing', value: results.summary.unusual_timing, color: '#f97316' },
                          { name: 'Round Num', value: results.summary.round_numbers, color: '#3b82f6' },
                          { name: 'Threshold', value: results.summary.threshold_flags, color: '#ef4444' },
                        ]}
                        margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
                        <XAxis dataKey="name" stroke="#525252" tick={{ fill: '#a3a3a3' }} axisLine={false} tickLine={false} />
                        <YAxis stroke="#525252" tick={{ fill: '#a3a3a3' }} axisLine={false} tickLine={false} />
                        <Tooltip
                          contentStyle={{ backgroundColor: '#171717', border: '1px solid #404040', borderRadius: '8px', color: '#fff' }}
                          cursor={{ fill: 'transparent' }}
                        />
                        <Bar dataKey="value" radius={[4, 4, 0, 0]} barSize={50}>
                          {
                            [
                              { name: 'Duplicates', value: results.summary.duplicates, color: '#a855f7' },
                              { name: 'Timing', value: results.summary.unusual_timing, color: '#f97316' },
                              { name: 'Round Num', value: results.summary.round_numbers, color: '#3b82f6' },
                              { name: 'Threshold', value: results.summary.threshold_flags, color: '#ef4444' },
                            ].map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))
                          }
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Details Tab */}
                <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 flex flex-col">
                  <h3 className="text-lg font-semibold text-white mb-4">Risk Breakdown</h3>
                  <div className="flex-1 overflow-y-auto pr-2 space-y-3">
                    {/* Render duplicates list if any */}
                    {results.summary.duplicates > 0 && (
                      <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg">
                        <p className="text-sm font-medium text-purple-400 mb-1">Potential Duplicate Payments</p>
                        <p className="text-xs text-neutral-400">Found {results.summary.duplicates} identical values.</p>
                      </div>
                    )}
                    {results.summary.unusual_timing > 0 && (
                      <div className="p-3 bg-orange-500/10 border border-orange-500/20 rounded-lg">
                        <p className="text-sm font-medium text-orange-400 mb-1">Weekend Activity</p>
                        <p className="text-xs text-neutral-400">{results.summary.unusual_timing} transactions on Sat/Sun.</p>
                      </div>
                    )}
                    {results.summary.round_numbers > 0 && (
                      <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                        <p className="text-sm font-medium text-blue-400 mb-1">Round Number Abuse</p>
                        <p className="text-xs text-neutral-400">{results.summary.round_numbers} clean multiples of 1,000.</p>
                      </div>
                    )}
                    {results.summary.threshold_flags > 0 && (
                      <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                        <p className="text-sm font-medium text-red-400 mb-1">Approval Evasion</p>
                        <p className="text-xs text-neutral-400">{results.summary.threshold_flags} transactions just below limit.</p>
                      </div>
                    )}

                    {results.summary.duplicates === 0 && results.summary.unusual_timing === 0 && results.summary.round_numbers === 0 && results.summary.threshold_flags === 0 && (
                      <div className="flex flex-col items-center justify-center h-40 text-neutral-500">
                        <CheckCircle className="w-8 h-8 mb-2 opacity-50" />
                        <p className="text-sm">No anomalies detected.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

function StatCard({ label, value, icon, color }: { label: string, value: number, icon: React.ReactNode, color: string }) {
  return (
    <div className="p-6 bg-neutral-900 border border-neutral-800 rounded-xl hover:border-neutral-700 transition-colors">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-2 rounded-lg bg-${color}-500/10`}>
          {icon}
        </div>
        <span className="text-2xl font-bold text-white">{value}</span>
      </div>
      <p className="text-sm text-neutral-400">{label}</p>
    </div>
  );
}
