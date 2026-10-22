import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CredSure AI | Commercial Credit Decisioning & Underwriting",
  description:
    "Institutional credit risk scorecard and underwriting platform. Transparent Weight of Evidence scoring, Basel III metrics, and autonomous loan committee decisioning.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="icon"
          href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23C56A4A'><path d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'/></svg>"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
