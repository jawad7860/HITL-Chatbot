import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HITL Chatbot",
  description:
    "A memory-enabled chatbot with Human-in-the-Loop tool approval, built on LangChain + LangGraph.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full">{children}</body>
    </html>
  );
}
