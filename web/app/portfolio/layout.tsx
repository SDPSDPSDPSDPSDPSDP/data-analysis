// Portfolio shows the site in dark mode, without touching the visitor's stored choice.
export default function PortfolioLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <script dangerouslySetInnerHTML={{ __html: `document.documentElement.dataset.theme = "dark";` }} />
      {children}
    </>
  );
}
