import './globals.css';
import { config } from '@fortawesome/fontawesome-svg-core';
import '@fortawesome/fontawesome-svg-core/styles.css';
config.autoAddCss = false;

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <title>Fraud Prediction</title>
        <meta name="description" content="Fraud prediction application" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="font-['Inter']">{children}</body>
    </html>
  );
} 