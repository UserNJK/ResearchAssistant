import "./globals.css";

export const metadata = {
  title: "ResearchAssistantAgent",
  description: "AI-powered research assistant"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}