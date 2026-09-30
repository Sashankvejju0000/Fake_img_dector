function Stat({ label, value, tone = 'text-slate-100' }) {
  return (
    <div className="rounded-3xl bg-slate-950/80 p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className={`mt-2 text-2xl font-semibold ${tone}`}>{value}</p>
    </div>
  )
}

export default function SummaryStats({ result }) {
  const s = result.summary
  if (!s) return null

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Analysis Summary</p>
          <p className="mt-2 text-xl font-semibold text-slate-100">{s.verdict}</p>
          {result.website && <p className="mt-1 break-all text-sm text-slate-500">{result.website}</p>}
        </div>
        <div className="text-right text-xs text-slate-500">
          {result.elapsed_seconds != null && <p>{result.elapsed_seconds}s</p>}
          {result.cached && <p className="text-cyan-400">served from cache</p>}
        </div>
      </div>

      <div className="mt-5 h-3 w-full overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full bg-gradient-to-r from-rose-500 to-orange-400"
          style={{ width: `${s.ai_percentage}%` }}
        />
      </div>
      <p className="mt-2 text-sm text-slate-400">{s.ai_percentage}% of analyzed images look AI-generated</p>

      <div className="mt-5 grid gap-4 sm:grid-cols-4">
        <Stat label="Total images" value={result.total_images} />
        <Stat label="AI-generated" value={s.ai_count} tone="text-rose-400" />
        <Stat label="Real" value={s.real_count} tone="text-emerald-400" />
        <Stat label="Uncertain" value={s.uncertain_count + s.unknown_count} tone="text-amber-400" />
      </div>
    </div>
  )
}
