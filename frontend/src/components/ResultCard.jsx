export default function ResultCard({ filename, prediction, confidence, imageUrl }) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900 p-5 shadow-soft">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-slate-400">Filename</p>
          <p className="text-lg font-semibold text-slate-100">{filename}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase tracking-[0.16em] text-slate-300">
            {prediction ?? 'PENDING'}
          </span>
          {confidence != null && (
            <span className="text-sm text-slate-400">{confidence.toFixed(2)}%</span>
          )}
        </div>
      </div>
      {imageUrl && (
        <img
          src={imageUrl}
          alt={filename}
          className="mt-4 h-56 w-full rounded-3xl object-cover border border-slate-800"
        />
      )}
    </div>
  )
}
