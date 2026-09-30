import { useState } from 'react'

const TONES = {
  AI: { badge: 'bg-rose-500/15 text-rose-300 border-rose-500/40', bar: 'bg-rose-500', text: 'AI-generated' },
  REAL: { badge: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40', bar: 'bg-emerald-500', text: 'Real' },
  UNCERTAIN: { badge: 'bg-amber-500/15 text-amber-300 border-amber-500/40', bar: 'bg-amber-500', text: 'Uncertain' },
  UNKNOWN: { badge: 'bg-slate-700/40 text-slate-300 border-slate-600', bar: 'bg-slate-500', text: 'Unreadable' },
}

export default function ResultCard({ image, previewSrc }) {
  const { filename, prediction, confidence, ai_probability, real_probability, heatmap, width, height } = image
  const [showHeatmap, setShowHeatmap] = useState(false)
  const [broken, setBroken] = useState(false)

  const tone = TONES[prediction] || TONES.UNKNOWN
  const baseSrc = previewSrc || image.image_url
  const src = showHeatmap && heatmap ? heatmap : baseSrc

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900 p-5 shadow-soft">
      {src && !broken ? (
        <img
          src={src}
          alt={filename}
          loading="lazy"
          referrerPolicy="no-referrer"
          onError={() => setBroken(true)}
          className="h-56 w-full rounded-2xl border border-slate-800 object-cover"
        />
      ) : (
        <div className="flex h-56 w-full items-center justify-center rounded-2xl border border-slate-800 bg-slate-950 text-sm text-slate-500">
          Preview unavailable (the site blocks hot-linking)
        </div>
      )}

      <div className="mt-4 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-slate-200" title={filename}>{filename}</p>
          {width && height && <p className="text-xs text-slate-500">{width} × {height}px</p>}
        </div>
        <span className={`shrink-0 rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wider ${tone.badge}`}>
          {tone.text}
        </span>
      </div>

      {confidence != null && (
        <div className="mt-4">
          <div className="flex justify-between text-xs text-slate-400">
            <span>Confidence</span>
            <span>{confidence.toFixed(1)}%</span>
          </div>
          <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-slate-800">
            <div className={`h-full ${tone.bar}`} style={{ width: `${confidence}%` }} />
          </div>
          {ai_probability != null && (
            <p className="mt-2 text-xs text-slate-500">
              AI {ai_probability.toFixed(1)}% · Real {real_probability.toFixed(1)}%
            </p>
          )}
        </div>
      )}

      <div className="mt-4 flex flex-wrap gap-3 text-xs">
        {heatmap && (
          <button
            type="button"
            onClick={() => setShowHeatmap((v) => !v)}
            className="rounded-full border border-cyan-500/40 px-3 py-1 text-cyan-300 hover:bg-cyan-500/10"
          >
            {showHeatmap ? 'Show original' : 'Show heat-map (Grad-CAM)'}
          </button>
        )}
        {image.image_url && (
          <a
            href={image.image_url}
            target="_blank"
            rel="noreferrer"
            className="rounded-full border border-slate-700 px-3 py-1 text-slate-300 hover:bg-slate-800"
          >
            Open original
          </a>
        )}
      </div>
    </div>
  )
}
