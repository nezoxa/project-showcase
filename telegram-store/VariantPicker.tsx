import { useCallback, useEffect, useMemo, useState } from 'react';
import { useCart, type CatalogItem } from './CartContext';
import { ProductImage } from './ProductImage';
import type { ProductVariantDto } from './variant-service';

interface VariantPickerProps {
  item: CatalogItem & { name: string; imageUrl?: string };
  variants: readonly ProductVariantDto[];
  onAdded?: () => void;
}

export function VariantPicker(props: VariantPickerProps) {
  return <VariantChoices key={props.item.id} {...props} />;
}

function VariantChoices({ item, variants, onAdded }: VariantPickerProps) {
  const cart = useCart();
  const [selected, setSelected] = useState<Record<string, string>>({});
  const [justAdded, setJustAdded] = useState(false);

  const dimensions = useMemo(() => {
    const keys: string[] = [];
    for (const variant of variants) {
      for (const key of Object.keys(variant.characteristics)) {
        if (!keys.includes(key)) keys.push(key);
      }
    }
    return keys;
  }, [variants]);

  const optionsFor = useCallback(
    (dimensionIndex: number): string[] => {
      const priorKeys = dimensions.slice(0, dimensionIndex);
      const matching = variants.filter((v) => priorKeys.every((key) => v.characteristics[key] === selected[key]));
      return [...new Set(matching.map((v) => v.characteristics[dimensions[dimensionIndex]]).filter(Boolean))];
    },
    [dimensions, selected, variants],
  );

  // Автовыбор единственного доступного значения характеристики.
  useEffect(() => {
    for (let i = 0; i < dimensions.length; i++) {
      const key = dimensions[i];
      if (selected[key]) continue;
      const options = optionsFor(i);
      if (options.length === 1) {
        setSelected((prev) => ({ ...prev, [key]: options[0] }));
      }
      break;
    }
  }, [dimensions, optionsFor, selected]);

  function choose(dimensionIndex: number, value: string) {
    const key = dimensions[dimensionIndex];
    const next: Record<string, string> = {};
    for (let i = 0; i < dimensionIndex; i++) next[dimensions[i]] = selected[dimensions[i]];
    next[key] = value;
    setSelected(next);
    setJustAdded(false);
  }

  const matchedVariant = dimensions.every((key) => selected[key])
    ? variants.find((v) => dimensions.every((key) => v.characteristics[key] === selected[key])) ?? null
    : null;

  function addToCart() {
    if (!matchedVariant || matchedVariant.available <= 0) return;
    cart.add(item, {
      id: matchedVariant.id,
      label: dimensions.map((key) => selected[key]).join(', '),
      priceRub: matchedVariant.priceRub,
      available: matchedVariant.available,
    });
    setJustAdded(true);
    onAdded?.();
  }

  return (
    <section>
      <h2>{item.name}</h2>
      {item.imageUrl && <ProductImage src={item.imageUrl} alt={item.name} />}

      {dimensions.map((key, i) => {
        const decidedBefore = dimensions.slice(0, i).every((prior) => selected[prior]);
        if (!decidedBefore) return null;
        return (
          <fieldset key={key}>
            <legend>{key}</legend>
            {optionsFor(i).map((value) => (
              <button key={value} type="button" aria-pressed={selected[key] === value} onClick={() => choose(i, value)}>
                {value}
              </button>
            ))}
          </fieldset>
        );
      })}

      {matchedVariant && (
        <p>
          {matchedVariant.priceRub.toLocaleString('ru-BY', { style: 'currency', currency: 'BYN' })}
          {' · '}
          {matchedVariant.available <= 0 ? 'Нет в наличии' : 'В наличии'}
        </p>
      )}
      <button type="button" disabled={!matchedVariant || matchedVariant.available <= 0} onClick={addToCart}>
        {justAdded ? 'Добавлено' : 'Добавить в корзину'}
      </button>
    </section>
  );
}
