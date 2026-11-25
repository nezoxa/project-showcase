import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

export interface CatalogItem {
  id: string;
  priceRub: number;
  available: number;
}

const CART_STORAGE_KEY = 'portfolio-cart-v1';

export interface CartVariant {
  id: string;
  label: string;
  priceRub: number;
  available: number;
}

interface CartLine {
  item: CatalogItem;
  variant?: CartVariant;
  quantity: number;
}

function lineId(item: CatalogItem, variant?: CartVariant): string {
  return variant ? `${item.id}:${variant.id}` : item.id;
}

function linePrice(line: CartLine): number {
  return line.variant?.priceRub ?? line.item.priceRub;
}

function lineAvailable(line: CartLine): number {
  return line.variant?.available ?? line.item.available;
}

interface CartContextValue {
  lines: CartLine[];
  add: (item: CatalogItem, variant?: CartVariant, quantity?: number) => void;
  remove: (id: string) => void;
  setQuantity: (id: string, quantity: number) => void;
  clear: () => void;
  totalRub: number;
  totalCount: number;
  linePrice: typeof linePrice;
  lineAvailable: typeof lineAvailable;
}

const CartContext = createContext<CartContextValue | null>(null);

function loadStoredLines(): CartLine[] {
  try {
    const raw = localStorage.getItem(CART_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function CartProvider({ children }: { children: ReactNode }) {
  // Telegram WebView часто выгружает приложение при переключении чатов — без сохранения
  // в localStorage корзина молча обнулялась при каждом таком сворачивании.
  const [lines, setLines] = useState<CartLine[]>(loadStoredLines);

  useEffect(() => {
    try {
      localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(lines));
    } catch {
      // приватный режим/квота — корзина просто не переживёт перезапуск, не критично
    }
  }, [lines]);

  const value = useMemo<CartContextValue>(() => {
    const add = (item: CatalogItem, variant?: CartVariant, quantity = 1) => {
      const id = lineId(item, variant);
      const available = variant?.available ?? item.available;
      if (available <= 0) return;
      setLines((prev) => {
        const existing = prev.find((l) => lineId(l.item, l.variant) === id);
        if (existing) {
          const nextQuantity = Math.min(existing.quantity + quantity, available);
          return prev.map((l) => (lineId(l.item, l.variant) === id ? { ...l, quantity: nextQuantity } : l));
        }
        return [...prev, { item, variant, quantity: Math.min(quantity, available) }];
      });
    };

    const remove = (id: string) => {
      setLines((prev) => prev.filter((l) => lineId(l.item, l.variant) !== id));
    };

    const setQuantity = (id: string, quantity: number) => {
      setLines((prev) => {
        if (quantity <= 0) return prev.filter((l) => lineId(l.item, l.variant) !== id);
        return prev.map((l) =>
          lineId(l.item, l.variant) === id ? { ...l, quantity: Math.min(quantity, lineAvailable(l)) } : l,
        );
      });
    };

    const clear = () => setLines([]);

    const totalRub = lines.reduce((sum, l) => sum + linePrice(l) * l.quantity, 0);
    const totalCount = lines.reduce((sum, l) => sum + l.quantity, 0);

    return { lines, add, remove, setQuantity, clear, totalRub, totalCount, linePrice, lineAvailable };
  }, [lines]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart(): CartContextValue {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart должен использоваться внутри CartProvider');
  return ctx;
}

export { lineId };
