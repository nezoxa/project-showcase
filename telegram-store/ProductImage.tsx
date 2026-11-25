import { useEffect, useRef, useState } from 'react';
import './product-image.css';

/* Откладывает загрузку изображения до приближения карточки к видимой области. */
export function ProductImage({ src, alt }: { src?: string; alt: string }) {
  const [visible, setVisible] = useState(false);
  const [failed, setFailed] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    if (typeof IntersectionObserver === 'undefined') {
      setVisible(true);
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { rootMargin: '400px 0px' },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // Смена товара (например, при переиспользовании DOM-узла в списке) должна сбрасывать
  // предыдущую ошибку — иначе новая картинка того же <div> навсегда осталась бы плейсхолдером.
  useEffect(() => {
    setFailed(false);
  }, [src]);

  const showImage = Boolean(src) && !failed && visible;

  return (
    <div ref={containerRef} className="product-image-frame">
      {showImage ? (
        <>
          <img className="product-image-bg" src={src} alt="" aria-hidden="true" loading="lazy" decoding="async" />
          <img
            className="product-image"
            src={src}
            alt={alt}
            loading="lazy"
            decoding="async"
            onError={() => setFailed(true)}
          />
        </>
      ) : (
        <div className="product-image-placeholder" aria-hidden="true">
          📦
        </div>
      )}
    </div>
  );
}
