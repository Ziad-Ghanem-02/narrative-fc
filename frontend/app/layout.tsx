import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Rise of the Underdogs",
  description: "An interactive World Cup data storytelling study",
  icons: {
    icon: "/football_favicon.png",
    shortcut: "/football_favicon.png",
    apple: "/football_favicon.png"
  }
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
