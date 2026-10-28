const ALLOWED_API = new Set([
  "GET /api/info",
  "GET /api/health-all",
  "GET /api/catalog",
  "GET /api/audit",
  "GET /api/whoami",
  // Future, only after explicit approval:
  // "POST /api/qdrant/query",
]);

function timingSafeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string") {
    return false;
  }

  const encoder = new TextEncoder();
  const ab = encoder.encode(a);
  const bb = encoder.encode(b);

  if (ab.length !== bb.length) {
    return false;
  }

  let diff = 0;
  for (let i = 0; i < ab.length; i++) {
    diff |= ab[i] ^ bb[i];
  }

  return diff === 0;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      return Response.json({
        status: "ok",
        worker: "trident-edge",
        version: "1.1.0",
        timestamp: new Date().toISOString(),
      });
    }

    if (!url.pathname.startsWith("/api/")) {
      return Response.json({ error: "not found" }, { status: 404 });
    }

    const auth = request.headers.get("Authorization") || "";
    const token = auth.startsWith("Bearer ") ? auth.slice(7) : null;

    if (!env.TRIDENT_EDGE_TOKEN) {
      return Response.json({ error: "edge token not configured" }, { status: 503 });
    }

    if (!token || !timingSafeEqual(token, env.TRIDENT_EDGE_TOKEN)) {
      return Response.json({ error: "unauthorized" }, { status: 401 });
    }

    if (!env.ATLAS_BACKEND_URL) {
      return Response.json({ error: "backend not configured" }, { status: 503 });
    }

    if (!env.TRIDENT_AGENT_KEY) {
      return Response.json({ error: "backend agent key not configured" }, { status: 503 });
    }

    const policyKey = request.method + " " + url.pathname;

    if (!ALLOWED_API.has(policyKey)) {
      return Response.json(
        { error: "endpoint not allowed by edge policy" },
        { status: 403 }
      );
    }

    const backendBase = String(env.ATLAS_BACKEND_URL).replace(/\/+$/, "");
    const target = new URL(backendBase + url.pathname + url.search);

    const backendHeaders = new Headers();

    const accept = request.headers.get("Accept");
    if (accept) {
      backendHeaders.set("Accept", accept);
    }

    const contentType = request.headers.get("Content-Type");
    if (contentType) {
      backendHeaders.set("Content-Type", contentType);
    }

    backendHeaders.set("X-API-Key", env.TRIDENT_AGENT_KEY);

    const init = {
      method: request.method,
      headers: backendHeaders,
    };

    if (!["GET", "HEAD"].includes(request.method)) {
      init.body = request.body;
      init.duplex = "half";
    }

    let upstream;

    try {
      upstream = await fetch(target.toString(), init);
    } catch (e) {
      return Response.json({ error: "backend unreachable" }, { status: 502 });
    }

    const responseHeaders = new Headers();

    for (const [key, value] of upstream.headers.entries()) {
      const lk = key.toLowerCase();

      // Evita header hop-by-hop / length mismatch quando si rigenera la Response.
      if (
        lk === "content-length" ||
        lk === "content-encoding" ||
        lk === "transfer-encoding" ||
        lk === "connection" ||
        lk === "keep-alive"
      ) {
        continue;
      }

      responseHeaders.set(key, value);
    }

    responseHeaders.set("X-Trident-Edge", "1.1.0");

    return new Response(upstream.body, {
      status: upstream.status,
      statusText: upstream.statusText,
      headers: responseHeaders,
    });
  },
};
