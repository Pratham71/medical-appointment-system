import { spawn } from "node:child_process";
import process from "node:process";

const isWindows = process.platform === "win32";

const commands = [
  {
    name: "backend",
    command: "uv",
    args: [
      "run",
      "uvicorn",
      "app.backend.app.main:app",
      "--reload",
      "--host",
      "127.0.0.1",
      "--port",
      "8000",
    ],
  },
  {
    name: "frontend",
    command: "npm",
    args: ["--prefix", "app/frontend", "run", "dev"],
    env: {
      BACKEND_API_URL: process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000",
    },
  },
];

const children = [];
let shuttingDown = false;

function pipeWithPrefix(stream, name, output) {
  let buffer = "";

  stream.on("data", (chunk) => {
    buffer += chunk.toString();
    const lines = buffer.split(/\r?\n/);
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.length > 0) output.write(`[${name}] ${line}\n`);
    }
  });

  stream.on("end", () => {
    if (buffer.length > 0) output.write(`[${name}] ${buffer}\n`);
  });
}

function stopChild(child) {
  if (!child.pid || child.killed) return;

  if (isWindows) {
    spawn("taskkill", ["/pid", String(child.pid), "/t", "/f"], {
      stdio: "ignore",
    });
    return;
  }

  child.kill("SIGTERM");
}

function shutdown(exitCode = 0) {
  if (shuttingDown) return;
  shuttingDown = true;

  for (const child of children) stopChild(child);

  setTimeout(() => process.exit(exitCode), 300);
}

for (const item of commands) {
  let child;

  try {
    child = spawn(item.command, item.args, {
      cwd: process.cwd(),
      env: { ...process.env, ...(item.env ?? {}) },
      shell: isWindows,
      stdio: ["inherit", "pipe", "pipe"],
      windowsHide: true,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`[${item.name}] failed to start: ${message}`);
    shutdown(1);
    break;
  }

  children.push(child);
  pipeWithPrefix(child.stdout, item.name, process.stdout);
  pipeWithPrefix(child.stderr, item.name, process.stderr);

  child.on("error", (error) => {
    console.error(`[${item.name}] failed to start: ${error.message}`);
    shutdown(1);
  });

  child.on("exit", (code, signal) => {
    if (shuttingDown) return;
    const reason = signal ? `signal ${signal}` : `code ${code}`;
    console.error(`[${item.name}] exited with ${reason}; stopping dev servers.`);
    shutdown(code ?? 1);
  });
}

process.on("SIGINT", () => shutdown(0));
process.on("SIGTERM", () => shutdown(0));
