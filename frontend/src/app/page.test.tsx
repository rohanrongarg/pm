import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Home from "@/app/page";
import { initialData } from "@/lib/kanban";

vi.mock("@/components/KanbanBoard", () => ({
  KanbanBoard: ({
    onBoardChange,
    board,
  }: {
    onBoardChange?: (next: typeof initialData) => void;
    board?: typeof initialData;
  }) => (
    <div data-testid="mock-board">
      <button
        type="button"
        onClick={() => {
          if (!board || !onBoardChange) {
            return;
          }
          onBoardChange({
            ...board,
            columns: board.columns.map((column, index) =>
              index === 0 ? { ...column, title: "Inbox" } : column
            ),
          });
        }}
      >
        Trigger board save
      </button>
    </div>
  ),
}));

type JsonValue = Record<string, unknown> | Array<unknown>;

const jsonResponse = (body: JsonValue, ok = true, status = 200): Response =>
  ({
    ok,
    status,
    json: async () => body,
  }) as Response;

describe("Home page auth and chat", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows login error when credentials are rejected", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ authenticated: false }))
      .mockResolvedValueOnce(
        jsonResponse({ detail: "Invalid username or password." }, false, 401)
      );

    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    await screen.findByRole("heading", { name: /sign in/i });
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(
      await screen.findByText("Invalid username or password.")
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/api/auth/login",
      expect.objectContaining({
        method: "POST",
      })
    );
  });

  it("sends chat request and renders assistant reply", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({ authenticated: true, username: "user" })
      )
      .mockResolvedValueOnce(jsonResponse(initialData))
      .mockResolvedValueOnce(
        jsonResponse({
          message: "Done. Updated board.",
          board: initialData,
        })
      );

    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    await screen.findByText("AI Assistant");
    await userEvent.type(
      screen.getByPlaceholderText(/ask the assistant to update the board/i),
      "Move card 1"
    );
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText("Done. Updated board.")).toBeInTheDocument();

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/ai/chat",
        expect.objectContaining({
          method: "POST",
        })
      );
    });
  });
});
