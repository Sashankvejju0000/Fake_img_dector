export default function UrlForm({ url, onChange, onSubmit, disabled }) {
  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4 sm:flex-row">
      <label className="sr-only" htmlFor="website-url">Website URL</label>
      <input
        id="website-url"
        type="url"
        value={url}
        onChange={onChange}
        placeholder="https://example.com"
        disabled={disabled}
        className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-500/20"
      />
      <button
        type="submit"
        disabled={disabled}
        className="inline-flex items-center justify-center rounded-2xl bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 shadow-soft hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-700"
      >
        Analyze
      </button>
    </form>
  )
}
