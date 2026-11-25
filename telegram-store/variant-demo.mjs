import { getVariantsForProduct } from './variant-service.ts';

const notebook = { meta: { href: '/products/notebook' } };
const variants = [
  {
    id: 'notebook-a5',
    product: notebook,
    characteristics: [{ name: 'Format', value: 'A5' }],
    salePrices: [{ value: 650 }],
  },
  {
    id: 'notebook-a6',
    product: notebook,
    characteristics: [{ name: 'Format', value: 'A6' }],
    salePrices: [{ value: 520 }],
  },
  {
    id: 'notebook-archived',
    product: notebook,
    archived: true,
  },
];
const stock = [{ meta: { href: '/variants/notebook-a5' }, quantity: 4, salePrice: 590 }];

console.log(JSON.stringify(getVariantsForProduct('notebook', variants, stock), null, 2));
