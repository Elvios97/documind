import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";

const api = vi.hoisted(() => ({
  askWithRag: vi.fn(),
  cancelDocumentIndexing: vi.fn(),
  deleteDocument: vi.fn(),
  getDocumentSourceUrl: vi.fn(() => "http://127.0.0.1:8000/source"),
  getHealth: vi.fn(),
  listDocuments: vi.fn(),
  retryDocumentIndexing: vi.fn(),
  uploadPdf: vi.fn(),
}));

vi.mock("./api", () => api);

const documentSummary = {
  document_id: "doc-1",
  filename: "strategie.pdf",
  page_count: 12,
  created_at: "2026-05-20T12:00:00Z",
  indexing_status: "ready" as const,
  indexing_error: null,
  indexing_completed_chunks: 12,
  indexing_total_chunks: 12,
  indexing_queue_position: null,
  indexing_active: false,
};

describe("App", () => {
  beforeEach(() => {
    window.localStorage.clear();
    api.getHealth.mockResolvedValue({ status: "ok", message: "online" });
    api.listDocuments.mockResolvedValue([]);
    api.uploadPdf.mockReset();
    api.askWithRag.mockReset();
    api.cancelDocumentIndexing.mockReset();
    api.deleteDocument.mockReset();
    api.retryDocumentIndexing.mockReset();
  });

  it("zeigt den leeren Startzustand und einen erreichbaren Backendstatus", async () => {
    render(<App />);

    expect(await screen.findByText("Noch keine lokal gespeicherten PDFs.")).toBeInTheDocument();
    expect(await screen.findByText("Backend online")).toBeInTheDocument();
    expect(screen.getByText("Bereit für deine PDFs")).toBeInTheDocument();
  });

  it("zeigt einen verständlichen Offlinezustand", async () => {
    api.getHealth.mockRejectedValue(new Error("offline"));
    api.listDocuments.mockRejectedValue(new Error("offline"));

    render(<App />);

    expect(await screen.findByText("Backend offline")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent("Dokumentenliste konnte nicht geladen werden.");
  });

  it("lädt ein PDF hoch und meldet die abgeschlossene Indexierung", async () => {
    api.uploadPdf.mockResolvedValue({
      document_id: "doc-2",
      filename: "bericht.pdf",
      page_count: 4,
      full_text: "Inhalt",
      indexing_status: "indexing",
      indexing_completed_chunks: 0,
      indexing_total_chunks: 0,
      indexing_queue_position: null,
      indexing_active: false,
    });
    const user = userEvent.setup();
    const { container } = render(<App />);
    await screen.findByText("Noch keine lokal gespeicherten PDFs.");

    const file = new File(["pdf"], "bericht.pdf", { type: "application/pdf" });
    const input = container.querySelector<HTMLInputElement>('input[type="file"]');
    expect(input).not.toBeNull();
    await user.upload(input!, file);

    expect(await screen.findByRole("status")).toHaveTextContent("Die Indexierung läuft im Hintergrund.");
    expect(screen.getAllByText(/4 Seiten/).length).toBeGreaterThan(0);
    expect(api.uploadPdf).toHaveBeenCalledWith(file);
    expect(screen.getByPlaceholderText("Indexierung abwarten")).toBeDisabled();
  });

  it("stellt eine RAG-Frage und öffnet die zugehörige Quelle", async () => {
    api.listDocuments.mockResolvedValue([documentSummary]);
    api.askWithRag.mockResolvedValue({
      document_ids: ["doc-1"],
      question: "Welche Risiken gibt es?",
      answer: "**Risiko:** Lieferengpass",
      model: "llama3",
      mode: "ask",
      sources: [{
        document_id: "doc-1",
        source_number: 1,
        filename: "strategie.pdf",
        page_number: 3,
        chunk_id: "chunk-3",
        score: 0.87,
        text_preview: "Ein möglicher Lieferengpass.",
      }, {
        document_id: "doc-2",
        source_number: 2,
        filename: "bericht.pdf",
        page_number: 7,
        chunk_id: "chunk-7",
        score: 0.81,
        text_preview: "Eine zweite relevante Quelle.",
      }],
    });
    const user = userEvent.setup();
    render(<App />);
    await screen.findAllByText("strategie.pdf");

    await user.type(screen.getByLabelText("Frage"), "Welche Risiken gibt es?");
    await user.click(screen.getByRole("button", { name: "Frage absenden" }));

    expect(await screen.findByText("Lieferengpass")).toBeInTheDocument();
    expect(screen.getByText("bericht.pdf")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /Quelle 1/ }));
    expect(screen.getByRole("dialog", { name: "PDF Quelle" })).toBeInTheDocument();
    expect(api.getDocumentSourceUrl).toHaveBeenCalledWith("doc-1", 3, "Ein möglicher Lieferengpass.");
    expect(api.askWithRag).toHaveBeenCalledWith(["doc-1"], "Welche Risiken gibt es?", 5, "ask");
  });

  it("wählt mehrere Dokumentkarten per Linksklick aus und wieder ab", async () => {
    const secondDocument = { ...documentSummary, document_id: "doc-2", filename: "bericht.pdf" };
    api.listDocuments.mockResolvedValue([documentSummary, secondDocument]);
    const user = userEvent.setup();
    render(<App />);
    await screen.findAllByText("strategie.pdf");

    const secondButton = screen.getByRole("button", { name: /bericht\.pdf12 Seiten/ });
    await user.click(secondButton);
    expect(secondButton).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("2 von 5")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "bericht.pdf aus Auswahl entfernen" })).toBeInTheDocument();

    await user.click(secondButton);
    expect(secondButton).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByText("1 von 5")).toBeInTheDocument();
  });

  it("stellt eine gespeicherte Auswahl wieder her und verwirft unbekannte IDs", async () => {
    const secondDocument = { ...documentSummary, document_id: "doc-2", filename: "bericht.pdf" };
    window.localStorage.setItem(
      "documind:selected-documents:v1",
      JSON.stringify({ version: 1, documentIds: ["doc-2", "nicht-mehr-vorhanden"] }),
    );
    api.listDocuments.mockResolvedValue([documentSummary, secondDocument]);

    render(<App />);

    const secondButton = await screen.findByRole("button", { name: /bericht\.pdf12 Seiten/ });
    expect(secondButton).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: /strategie\.pdf12 Seiten/ })).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByText("1 von 5")).toBeInTheDocument();
  });

  it("wechselt den Analysemodus und speichert Modus sowie Kontextlimit", async () => {
    api.listDocuments.mockResolvedValue([documentSummary]);
    const user = userEvent.setup();
    render(<App />);
    await screen.findAllByText("strategie.pdf");

    const compareButton = screen.getByRole("button", { name: "Vergleichen" });
    await user.click(compareButton);
    expect(compareButton).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("Welche Gemeinsamkeiten und Unterschiede gibt es?")).toBeInTheDocument();

    const topKInput = screen.getByLabelText("Anzahl der Kontextstellen");
    fireEvent.change(topKInput, { target: { value: "8" } });
    expect(JSON.parse(window.localStorage.getItem("documind:analysis-preferences:v1") ?? "{}")).toMatchObject({
      version: 1,
      mode: "compare",
      topK: 8,
    });
  });

  it("stellt gespeicherte Analysepraeferenzen wieder her", async () => {
    window.localStorage.setItem(
      "documind:analysis-preferences:v1",
      JSON.stringify({ version: 1, mode: "summarize", topK: 7 }),
    );
    api.listDocuments.mockResolvedValue([documentSummary]);

    render(<App />);

    expect(await screen.findByRole("button", { name: "Zusammenfassen" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByLabelText("Anzahl der Kontextstellen")).toHaveValue(7);
    expect(screen.getByText("Fasse jedes Dokument kurz zusammen und ziehe ein Gesamtfazit.")).toBeInTheDocument();
  });

  it("sortiert Dokumente und nutzt nach dem Laden den kompakten Uploadzustand", async () => {
    const olderDocument = {
      ...documentSummary,
      document_id: "doc-older",
      filename: "alpha.pdf",
      created_at: "2026-04-01T10:00:00Z",
    };
    const newerDocument = {
      ...documentSummary,
      document_id: "doc-newer",
      filename: "zeta.pdf",
      created_at: "2026-06-01T10:00:00Z",
    };
    api.listDocuments.mockResolvedValue([olderDocument, newerDocument]);
    const user = userEvent.setup();
    const { container } = render(<App />);
    await screen.findAllByText("zeta.pdf");

    expect(container.querySelector(".upload-panel.compact")).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText("Dokumente sortieren"), "name");

    const documentButtons = screen.getAllByRole("button", { name: /\.pdf12 Seiten/ });
    expect(documentButtons.map((button) => button.textContent)).toEqual([
      expect.stringContaining("alpha.pdf"),
      expect.stringContaining("zeta.pdf"),
    ]);
  });

  it("hebt die gesamte Dokumentauswahl auf", async () => {
    const secondDocument = { ...documentSummary, document_id: "doc-2", filename: "bericht.pdf" };
    api.listDocuments.mockResolvedValue([documentSummary, secondDocument]);
    const user = userEvent.setup();
    render(<App />);
    await screen.findAllByText("strategie.pdf");

    await user.click(screen.getByRole("button", { name: /bericht\.pdf12 Seiten/ }));
    await user.click(screen.getByRole("button", { name: "Auswahl aufheben" }));

    expect(screen.getByText("0/5")).toBeInTheDocument();
    expect(screen.getByLabelText("Frage")).toBeDisabled();
    expect(JSON.parse(window.localStorage.getItem("documind:selected-documents:v1") ?? "{}")).toMatchObject({
      version: 1,
      documentIds: [],
    });
  });

  it("begrenzt die Mehrfachauswahl auf fünf Dokumente", async () => {
    const loadedDocuments = Array.from({ length: 6 }, (_, index) => ({
      ...documentSummary,
      document_id: `doc-${index + 1}`,
      filename: `dokument-${index + 1}.pdf`,
    }));
    api.listDocuments.mockResolvedValue(loadedDocuments);
    const user = userEvent.setup();
    render(<App />);
    await screen.findAllByText("dokument-1.pdf");

    for (let index = 2; index <= 5; index += 1) {
      await user.click(screen.getByRole("button", { name: new RegExp(`dokument-${index}\\.pdf12 Seiten`) }));
    }
    expect(screen.getByText("5 von 5")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /dokument-6\.pdf12 Seiten/ }));
    expect(screen.getByRole("alert")).toHaveTextContent("hoechstens 5 Dokumente");
    expect(screen.getByText("5 von 5")).toBeInTheDocument();
  });

  it("durchsucht und filtert die Dokumentliste", async () => {
    const failedDocument = {
      ...documentSummary,
      document_id: "doc-failed",
      filename: "fehlerbericht.pdf",
      indexing_status: "failed" as const,
      indexing_error: "Testfehler",
    };
    api.listDocuments.mockResolvedValue([documentSummary, failedDocument]);
    const user = userEvent.setup();
    render(<App />);
    await screen.findAllByText("strategie.pdf");

    const searchInput = screen.getByLabelText("Dokumente durchsuchen");
    await user.type(searchInput, "fehler");
    expect(screen.getByRole("button", { name: /fehlerbericht\.pdf12 Seiten/ })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /strategie\.pdf12 Seiten/ })).not.toBeInTheDocument();

    await user.clear(searchInput);
    await user.selectOptions(screen.getByLabelText("Dokumentstatus filtern"), "attention");
    expect(screen.getByRole("button", { name: /fehlerbericht\.pdf12 Seiten/ })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /strategie\.pdf12 Seiten/ })).not.toBeInTheDocument();
  });

  it("löscht ein bestätigtes Dokument aus der Liste", async () => {
    api.listDocuments.mockResolvedValue([documentSummary]);
    api.deleteDocument.mockResolvedValue({ document_id: "doc-1", deleted: true });
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const user = userEvent.setup();
    render(<App />);
    await screen.findAllByText("strategie.pdf");

    await user.click(screen.getByRole("button", { name: "strategie.pdf löschen" }));

    await waitFor(() => expect(api.deleteDocument).toHaveBeenCalledWith("doc-1"));
    expect(screen.queryByText("strategie.pdf")).not.toBeInTheDocument();
  });

  it("zeigt Uploadfehler und entfernt einen veralteten Erfolgsstatus", async () => {
    api.uploadPdf.mockRejectedValue(new Error("Das Embedding-Modell fehlt."));
    const { container } = render(<App />);
    await screen.findByText("Noch keine lokal gespeicherten PDFs.");

    const input = container.querySelector<HTMLInputElement>('input[type="file"]');
    fireEvent.change(input!, {
      target: { files: [new File(["pdf"], "scan.pdf", { type: "application/pdf" })] },
    });

    expect(await screen.findByRole("alert")).toHaveTextContent("Das Embedding-Modell fehlt.");
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Datei erneut auswählen" })).toBeInTheDocument();
  });

  it("wiederholt eine fehlgeschlagene Frage mit erhaltener Eingabe", async () => {
    api.listDocuments.mockResolvedValue([documentSummary]);
    api.askWithRag
      .mockRejectedValueOnce(new Error("Ollama antwortet nicht rechtzeitig."))
      .mockResolvedValueOnce({
        document_ids: ["doc-1"],
        question: "Was ist wichtig?",
        answer: "Die belegte Antwort.",
        model: "llama3",
        mode: "ask",
        sources: [],
      });
    const user = userEvent.setup();
    render(<App />);
    await screen.findAllByText("strategie.pdf");

    await user.type(screen.getByLabelText("Frage"), "Was ist wichtig?");
    await user.click(screen.getByRole("button", { name: "Frage absenden" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Prüfe, ob Ollama läuft");

    await user.click(screen.getByRole("button", { name: "Frage erneut senden" }));
    expect(await screen.findByText("Die belegte Antwort.")).toBeInTheDocument();
    expect(api.askWithRag).toHaveBeenCalledTimes(2);
  });

  it("aktualisiert einen laufenden Indexierungsstatus automatisch", async () => {
    const indexingDocument = {
      ...documentSummary,
      indexing_status: "indexing" as const,
      indexing_completed_chunks: 0,
      indexing_total_chunks: 0,
      indexing_queue_position: 1,
      indexing_active: false,
    };
    api.listDocuments
      .mockResolvedValueOnce([indexingDocument])
      .mockResolvedValue([{ ...documentSummary, indexing_status: "ready" as const }]);
    vi.useFakeTimers();

    try {
      render(<App />);
      await vi.waitFor(() => expect(screen.getByText("Wartet · Position 1")).toBeInTheDocument());

      await vi.advanceTimersByTimeAsync(2000);

      await vi.waitFor(() => expect(screen.getByText("Bereit")).toBeInTheDocument());
      await vi.waitFor(() => expect(screen.getByLabelText("Frage")).toBeEnabled());
    } finally {
      vi.useRealTimers();
    }
  });

  it("bricht eine laufende Indexierung ab und bietet erneutes Indexieren an", async () => {
    const indexingDocument = {
      ...documentSummary,
      indexing_status: "indexing" as const,
      indexing_completed_chunks: 16,
      indexing_total_chunks: 40,
      indexing_active: true,
    };
    const cancelledDocument = {
      ...indexingDocument,
      indexing_status: "cancelled" as const,
      indexing_active: false,
      indexing_queue_position: null,
    };
    api.listDocuments.mockResolvedValue([indexingDocument]);
    api.cancelDocumentIndexing.mockResolvedValue(cancelledDocument);
    api.retryDocumentIndexing.mockResolvedValue({
      ...cancelledDocument,
      indexing_status: "indexing" as const,
      indexing_queue_position: 1,
    });
    const user = userEvent.setup();
    render(<App />);
    await screen.findByText("Wird indexiert: 16 / 40 Chunks");

    await user.click(screen.getByRole("button", { name: "strategie.pdf Indexierung abbrechen" }));
    expect(api.cancelDocumentIndexing).toHaveBeenCalledWith("doc-1");
    expect(await screen.findByText("Indexierung abgebrochen")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "strategie.pdf erneut indexieren" }));
    expect(api.retryDocumentIndexing).toHaveBeenCalledWith("doc-1");
    expect(await screen.findByText("Wartet · Position 1")).toBeInTheDocument();
  });
});
