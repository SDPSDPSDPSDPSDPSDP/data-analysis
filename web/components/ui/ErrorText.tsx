export default function ErrorText({ children }: { children: string }) {
  return <pre className="error" role="alert">{children}</pre>;
}
