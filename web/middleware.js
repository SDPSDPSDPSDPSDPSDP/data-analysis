// Vercel Routing Middleware, not Next middleware: `output: "export"` disables Next's. Needs the
// "Other" preset from vercel.json. Hides /portfolio behind the Portfolio site's ?t= embed token.
// Not security, just so nobody stumbles on it. next dev also picks this file up; skipped there so
// local stills keep working.
// Same-origin requests pass: in-frame navigation drops the ?t= the iframe src carried.
export const config = {
  matcher: ["/portfolio", "/portfolio/:path*"],
};

export default function middleware(request) {
  if (process.env.NODE_ENV === "development") return;
  if (request.headers.get("sec-fetch-site") === "same-origin") return;
  const expected = process.env.PORTFOLIO_EMBED_TOKEN;
  if (!expected) throw new Error("PORTFOLIO_EMBED_TOKEN must be set to serve /portfolio");
  if (new URL(request.url).searchParams.get("t") !== expected) {
    return new Response(null, { status: 404 });
  }
}
