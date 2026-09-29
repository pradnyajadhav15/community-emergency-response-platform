import "./globals.css";

import { AuthProvider } from "@/lib/auth";

export const metadata = {
  title: "CERP Admin",
  description: "Community Emergency Response Platform - administration portal",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}