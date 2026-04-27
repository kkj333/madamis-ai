import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, Mock } from 'vitest'
import ChatPage from '../app/page'

// fetch をモックする
global.fetch = vi.fn()

describe('ChatPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // StarField 内の IntersectionObserver など、ブラウザAPIが必要な場合はモックを追加
    window.HTMLElement.prototype.scrollIntoView = vi.fn()
  })

  it('初期状態でウェルカムメッセージが表示される', () => {
    render(<ChatPage />)
    expect(screen.getByText(/ようこそ、夢見師のもとへ。/)).toBeDefined()
  })

  it('ユーザーがメッセージを送信できる', async () => {
    // APIレスポンスのモック
    ;(global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ reply: 'あなたの夢は素晴らしいですね。' }),
    })

    render(<ChatPage />)
    
    const input = screen.getByPlaceholderText(/あなたの夢を語ってください/)
    const sendButton = screen.getByRole('button', { name: /送信/ })

    // メッセージを入力して送信
    fireEvent.change(input, { target: { value: '空を飛ぶ夢を見た' } })
    fireEvent.click(sendButton)

    // ユーザーの入力が表示されることを確認
    expect(screen.getByText('空を飛ぶ夢を見た')).toBeDefined()

    // バックエンドからの返答が表示されるのを待つ
    await waitFor(() => {
      expect(screen.getByText('あなたの夢は素晴らしいですね。')).toBeDefined()
    })
  })

  it('APIエラー時にエラーメッセージが表示される', async () => {
    // APIエラーのモック
    ;(global.fetch as Mock).mockResolvedValue({
      ok: false,
      status: 500,
    })

    render(<ChatPage />)
    
    const input = screen.getByPlaceholderText(/あなたの夢を語ってください/)
    const sendButton = screen.getByRole('button', { name: /送信/ })

    fireEvent.change(input, { target: { value: '怖い夢を見た' } })
    fireEvent.click(sendButton)

    // エラーメッセージが表示されるのを待つ
    await waitFor(() => {
      expect(screen.getByText(/夢と現実の境界で通信が途絶えました/)).toBeDefined()
    })
  })
})
