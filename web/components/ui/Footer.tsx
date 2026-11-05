import { REPO_URL } from "@/lib/site";

export default function Footer() {
  return (
    <footer className="site-footer">
      <span>shirin, SVG charts for pandas</span>
      <a href={REPO_URL} target="_blank" rel="noreferrer">
        GitHub
      </a>
    </footer>
  );
}
