import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Next.js の機能（navigation, router など）が必要な場合はここにモックを追加します
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
  }),
  useSearchParams: () => ({
    get: vi.fn(),
  }),
}))
