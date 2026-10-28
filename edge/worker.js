export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Health check pubblico (nessuna auth)
    if (url.pathname === "/health") {
      return Response.json({
        status: "ok",
        worker: "trident-edge",
        version: "1.0.0",
        timestamp: new Date().toISOString(),
      });
    }

    // Proxy API protetto (richiede Bearer token)
    if (url.pathname.startsWith("/api/")) {
      const auth = request.headers.get("Authorization") || "";
      const token = auth.startsWith("Bearer ") ? auth.slice(7) : null;

      if (!env.TRIDENT_EDGE_TOKEN) {
        return Response.json({ error: "edge token not configured" }, { status: 503 });
      }
      if (!token || token !== env.TRIDENT_EDGE_TOKEN) {
        return Response.json({ error: "unauthorized" }, { status: 401 });
      }
      if (!env.ATLAS_BACKEND_URL) {
        return Response.json({ error: "backend not configured" }, { status: 503 });
      }

      const path = url.pathname.replace(/^\/api/, "") || "/";
      const target = new URL(path + url.search, env.ATLAS_BACKEND_URL);
      return fetch(target.toString(), {
        method: request.method,
        headers: request.headers,
        body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
      });
    }

    return Response.json({ error: "not found" }, { status: 404 });
  },
};
