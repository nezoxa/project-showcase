export interface Variant {
  id: string;
  product: { meta: { href: string } };
  archived?: boolean;
  salePrices?: { value: number }[];
  characteristics?: { name: string; value: string }[];
}

export interface StockRow {
  meta: { href: string };
  quantity: number;
  salePrice?: number;
}

export interface ProductVariantDto {
  id: string;
  characteristics: Record<string, string>;
  priceRub: number;
  available: number;
}

/** Последний сегмент ссылки содержит идентификатор сущности. */
function idFromHref(href: string): string {
  return href.split('/').pop()!;
}

/** Группирует активные варианты по идентификатору родительского товара. */
export function groupVariantsByProductId(variants: readonly Variant[]): Map<string, Variant[]> {
  const map = new Map<string, Variant[]>();
  for (const variant of variants) {
    if (variant.archived) continue;
    const productId = idFromHref(variant.product.meta.href);
    if (!map.has(productId)) map.set(productId, []);
    map.get(productId)!.push(variant);
  }
  return map;
}

export function getVariantsForProduct(
  productId: string,
  variants: readonly Variant[],
  stockRows: readonly StockRow[],
): ProductVariantDto[] {
  const stockByAssortmentId = new Map(stockRows.map((row) => [idFromHref(row.meta.href), row]));
  const productVariants = groupVariantsByProductId(variants).get(productId) ?? [];

  return productVariants.map((variant) => {
    const stock = stockByAssortmentId.get(variant.id);
    const priceKopecks = stock?.salePrice ?? variant.salePrices?.[0]?.value ?? 0;
    const characteristics: Record<string, string> = {};
    for (const c of variant.characteristics ?? []) characteristics[c.name] = c.value;
    return {
      id: variant.id,
      characteristics,
      priceRub: priceKopecks / 100,
      available: stock?.quantity ?? 0,
    };
  });
}
