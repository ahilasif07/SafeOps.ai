import express from "express";
import path from "path";
import { spawn } from "child_process";
import { createProxyMiddleware } from "http-proxy-middleware";
import { createServer as createViteServer } from "vite";

async function startServer() {
  const app = express();
  const PORT = 3000;
  const FASTAPI_PORT = 8000;

  console.log("Starting SafeOps AI Python FastAPI Backend on port 8000...");
  const pythonProc = spawn("python3", ["-m", "uvicorn", "app.main:app", "--port", FASTAPI_PORT.toString(), "--host", "127.0.0.1"], {
    stdio: "inherit"
  });

  pythonProc.on("error", (err) => {
    console.error("Failed to start FastAPI process:", err);
  });

  // Proxy API requests to FastAPI
  const apiProxy = createProxyMiddleware({
    target: `http://127.0.0.1:${FASTAPI_PORT}`,
    changeOrigin: true,
  });

  app.use("/api", apiProxy);
  app.use("/docs", apiProxy);
  app.use("/redoc", apiProxy);
  app.use("/openapi.json", apiProxy);

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`SafeOps AI Enterprise Platform running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
