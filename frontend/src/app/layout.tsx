import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RailMind — Autonomous Railway Operations Center",
  description:
    "Multi-agent AI swarm for real-time railway incident detection, response orchestration, and predictive maintenance. From detection to resolution — zero human delay.",
  keywords: [
    "RailMind",
    "autonomous railway",
    "AI agents",
    "incident detection",
    "multi-agent system",
    "LangGraph",
    "railway operations",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
