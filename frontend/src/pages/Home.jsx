import { useMemo, useState } from 'react'
import UrlForm from '../components/UrlForm'
import UploadBox from '../components/UploadBox'
import Loader from '../components/Loader'
import ResultCard from '../components/ResultCard'
import SummaryStats from '../components/SummaryStats'
import { analyzeImageFile, analyzeWebsite, getErrorMessage } from '../services/api'

const FILTERS = ['ALL', 'AI', 'REAL', 'UNCERTAIN']

export default function Home() {
  const [mode, setMode] = useState('url')
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [previewSrc, setPreviewSrc] = useState(null)
  const [filter, setFilter] = useState('ALL')

  const run = async (task) => {
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const response = await task()
      setResult(response)
      setFilter('ALL')
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const handleUrlSubmit = (event) => {
    event.preventDefault()
    if (!url.trim()) {
      setError('Please enter a website URL.')
      return
    }
    setPreviewSrc(null)
    run(() => analyzeWebsite(url.trim()))
  }

  const handleFile = (file) => {
    if (!file.type.startsWith('image/')) {
      setError('Please choose an image file.')
      return
    }
    setPreviewSrc(URL.createObjectURL(file))
    run(() => analyzeImageFile(file))
  }

  const visibleImages = useMemo(() => {
    if (!result) return []
    if (filter === 'ALL') return result.images
    return result.images.filter((img) => img.prediction === filter)
  }, [result, filter])

  const tabClass = (active) =>
    `rounded-full px-5 py-2 text-sm font-medium ${
      active ? 'bg-cyan-500 text-slate-950' : 'bg-slate-900 text-slate-300 hover:bg-slate-800'
    }`

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col gap-10 px-6 py-10 sm:px-10">
      <section className="rounded-[2rem] border border-slate-800 bg-slate-950/90 p-8 shadow-soft sm:p-10">
        <p className="text-sm uppercase tracking-[0.35em] text-cyan-400/90">Fake AI Image Detector</p>
        <h1 className="mt-3 max-w-2xl text-4xl font-semibold text-slate-100 sm:text-5xl">
          Detect AI-generated images from any website or file.
        </h1>
        <p className="mt-4 max-w-2xl text-slate-400 sm:text-lg">
          Paste a page URL to scan every image on it, or upload a single image to see what the model focused on.
        </p>

        <div className="mt-8 flex gap-3">
          <button type="button" className={tabClass(mode === 'url')} onClick={() => setMode('url')}>
            Website URL
          </button>
          <button type="button" className={tabClass(mode === 'upload')} onClick={() => setMode('upload')}>
            Upload image
          </button>
        </div>

        <div className="mt-6">
          {mode === 'url' ? (
            <UrlForm
              url={url}
              onChange={(event) => setUrl(event.target.value)}
              onSubmit={handleUrlSubmit}
              disabled={loading}
            />
          ) : (
            <UploadBox onFile={handleFile} disabled={loading} />
          )}
        </div>

        {error && (
          <div role="alert" className="mt-6 rounded-3xl border border-red-500/20 bg-red-500/10 px-5 py-4 text-sm text-red-200">
            {error}
          </div>
        )}

        {loading && (
          <div className="text-center">
            <Loader />
            <p className="text-sm text-slate-500">
              {mode === 'url' ? 'Scraping and classifying images, this can take up to a minute…' : 'Analyzing image…'}
            </p>
          </div>
        )}

        {result && (
          <div className="mt-10 space-y-8">
            <SummaryStats result={result} />

            {result.images.length > 0 ? (
              <>
                <div className="flex flex-wrap gap-2">
                  {FILTERS.map((f) => (
                    <button
                      key={f}
                      type="button"
                      onClick={() => setFilter(f)}
                      className={`rounded-full border px-4 py-1.5 text-xs font-semibold uppercase tracking-wider ${
                        filter === f
                          ? 'border-cyan-400 bg-cyan-500/15 text-cyan-300'
                          : 'border-slate-700 text-slate-400 hover:bg-slate-800'
                      }`}
                    >
                      {f === 'ALL' ? `All (${result.images.length})` : f}
                    </button>
                  ))}
                </div>

                <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                  {visibleImages.map((image) => (
                    <ResultCard key={image.filename} image={image} previewSrc={previewSrc} />
                  ))}
                </section>
              </>
            ) : (
              <p className="text-center text-slate-400">{result.message}</p>
            )}
          </div>
        )}
      </section>

      <footer className="text-center text-sm text-slate-500">
        <p>EfficientNet-B0 classifier · results are probabilistic, not proof.</p>
      </footer>
    </main>
  )
}
