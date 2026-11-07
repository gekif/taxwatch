import "./globals.css";

export const metadata = {
  title: "TaxWatch",
  description: "Regional tax transaction monitoring",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
