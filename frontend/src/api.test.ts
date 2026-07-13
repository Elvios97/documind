import { afterEach, describe, expect, it, vi } from "vitest";

import { getHealth } from "./api";

describe("API client", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("übersetzt Netzwerkfehler in eine verständliche Backendmeldung", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    await expect(getHealth()).rejects.toThrow("Das lokale Backend ist nicht erreichbar");
  });

  it("übernimmt kontrollierte Fehlerdetails aus der API", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ detail: "Das Ollama-Modell 'llama3' ist nicht verfügbar." }),
      { status: 404, headers: { "Content-Type": "application/json" } },
    )));

    await expect(getHealth()).rejects.toThrow("Das Ollama-Modell 'llama3' ist nicht verfügbar.");
  });
});
