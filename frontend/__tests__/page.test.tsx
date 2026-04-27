import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import ChatPage from "../app/page";

global.fetch = vi.fn();

describe("ChatPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.HTMLElement.prototype.scrollIntoView = vi.fn();
  });

  it("初期状態でウェルカムメッセージが表示される", () => {
    render(<ChatPage />);
    expect(screen.getByText(/マーダーミステリー（マダミス）サポートへようこそ。/)).toBeDefined();
  });

  it("ユーザーがメッセージを送信できる", async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ reply: "議論ではメモを取ると整理しやすいです。" }),
    });

    render(<ChatPage />);

    const input = screen.getByPlaceholderText(/相談内容を入力/);
    const sendButton = screen.getByRole("button", { name: /送信/ });

    fireEvent.change(input, { target: { value: "初マダです。何を準備すればいい？" } });
    fireEvent.click(sendButton);

    expect(screen.getByText("初マダです。何を準備すればいい？")).toBeDefined();

    await waitFor(() => {
      expect(screen.getByText("議論ではメモを取ると整理しやすいです。")).toBeDefined();
    });
  });

  it("APIエラー時にエラーメッセージが表示される", async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: false,
      status: 500,
    });

    render(<ChatPage />);

    const input = screen.getByPlaceholderText(/相談内容を入力/);
    const sendButton = screen.getByRole("button", { name: /送信/ });

    fireEvent.change(input, { target: { value: "ルールがよくわからない" } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/HTTP 500/)).toBeDefined();
    });
  });
});
