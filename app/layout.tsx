import type { Metadata } from 'next'
import { Inter, Noto_Sans_SC } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import { Providers } from '@/components/providers'
import './globals.css'

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" })
const notoSansSC = Noto_Sans_SC({ subsets: ["latin"], weight: ["400", "500", "600", "700"], variable: "--font-noto" })

export const metadata: Metadata = {
  title: 'InsAgent Arena - Insurance Agent Evaluation Platform',
  description: 'The leading platform for evaluating and benchmarking insurance industry AI agents through standardized tests and live arena competitions.',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className={`${inter.variable} ${notoSansSC.variable} font-sans antialiased`}>
        <Providers>
          {children}
        </Providers>
        <Analytics />
      </body>
    </html>
  )
}
