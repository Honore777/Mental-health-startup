import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Amahoro Mental Wellness",
  description: "Professional AI mental wellness assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
