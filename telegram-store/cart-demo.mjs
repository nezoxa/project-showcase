const catalog = new Map([
  ["notebook", { title: "Notebook", priceMinor: 650, stock: 4 }],
  ["pen", { title: "Pen", priceMinor: 240, stock: 12 }],
]);

function summarizeCart(cart) {
  const items = [];
  let totalMinor = 0;

  for (const [id, quantity] of cart) {
    const product = catalog.get(id);
    if (!product || !Number.isSafeInteger(quantity) || quantity < 1 || quantity > product.stock) {
      throw new Error(`Invalid cart quantity or product: ${id}`);
    }

    const subtotalMinor = product.priceMinor * quantity;
    items.push({ title: product.title, quantity, subtotalMinor });
    totalMinor += subtotalMinor;
  }

  return { items, totalMinor, currency: "BYN" };
}

console.log(JSON.stringify(summarizeCart(new Map([["notebook", 2], ["pen", 3]])), null, 2));
