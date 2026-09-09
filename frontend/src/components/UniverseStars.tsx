import "../styles/universe-stars.css";

// Fixed, irregular positions avoid a tiled dot pattern and layout shifts.
const stars = (() => {
  let seed = 20260909;
  const random = () => {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    return seed / 4294967296;
  };
  return Array.from({ length: 112 }, (_, index) => ({
    left: `${(2 + random() * 96).toFixed(3)}%`,
    top: `${(2 + random() * 96).toFixed(3)}%`,
    size: index % 17 === 0 ? 2.4 : .8 + random() * .8,
    opacity: .22 + random() * .44,
    glow: index % 17 === 0,
    tone: index % 4,
  }));
})();

export default function UniverseStars() {
  return (
    <div className="universe-stars" aria-hidden="true">
      {stars.map((star, index) => (
        <i key={index} data-tone={star.tone} data-glow={star.glow || undefined} style={{
          left: star.left, top: star.top, width: star.size, height: star.size,
          opacity: star.opacity,
        }} />
      ))}
    </div>
  );
}
