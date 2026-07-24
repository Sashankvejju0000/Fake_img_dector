import { useState } from 'react'
import { ArrowRight } from 'lucide-react'
import UrlForm from '../components/UrlForm'
import Loader from '../components/Loader'
import ResultCard from '../components/ResultCard'
import { analyzeWebsite } from '../services/api'

export default function Home() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (!url) {
      setError('Please enter a website URL.')
      return
    }

    setLoading(true)

    try {
      const response = await analyzeWebsite(url)

      if (response.status === 'success') {
        setResult(response)
      } else {
        setError(response.message || 'Unexpected error from backend.')
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Request failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col gap-10 px-6 py-10 sm:px-10">
      <section className="rounded-[2rem] border border-slate-800 bg-slate-950/90 p-10 shadow-soft">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.35em] text-cyan-400/90">Fake AI Image Detector</p>
            <h1 className="mt-3 max-w-2xl text-4xl font-semibold text-slate-100 sm:text-5xl">
              Detect AI-generated images from any website.
            </h1>
            <p className="mt-4 max-w-2xl text-slate-400 sm:text-lg">
              Enter a website URL and receive scraped images with real-time predictions once the model is available.
            </p>
          </div>
          <div className="hidden rounded-[2rem] border border-slate-800 bg-slate-900/80 px-6 py-5 text-slate-300 shadow-soft sm:block">
            <p className="text-sm uppercase tracking-[0.32em] text-slate-500">Backend</p>
            <p className="mt-3 text-3xl font-semibold text-cyan-400">/analyze</p>
            <p className="mt-2 text-sm text-slate-400">POST request with a website URL.</p>
          </div>
        </div>

        <div className="mt-10">
          <UrlForm
            url={url}
            onChange={(event) => setUrl(event.target.value)}
            onSubmit={handleSubmit}
            disabled={loading}
          />
        </div>

        {error && (
          <div className="mt-6 rounded-3xl border border-red-500/20 bg-red-500/10 px-5 py-4 text-sm text-red-200">
            {error}
          </div>
        )}

        {loading && <Loader />}

        {result && (
          <div className="mt-10 space-y-8">
            <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6">
              <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Analysis Summary</p>
              <div className="mt-4 grid gap-4 sm:grid-cols-3">
                <div className="rounded-3xl bg-slate-950/80 p-5">
                  <p className="text-sm text-slate-400">Website</p>
                  <p className="mt-2 text-base text-slate-100">{result.website}</p>
                </div>
                <div className="rounded-3xl bg-slate-950/80 p-5">
                  <p className="text-sm text-slate-400">Total Images</p>
                  <p className="mt-2 text-base text-slate-100">{result.total_images}</p>
                </div>
                <div className="rounded-3xl bg-slate-950/80 p-5">
                  <p className="text-sm text-slate-400">Status</p>
                  <p className="mt-2 text-base text-slate-100">{result.message}</p>
                </div>
              </div>
            </div>

            <section className="grid gap-6 xl:grid-cols-2">
              {result.images.map((image) => (
                <ResultCard
                  key={image.filename}
                  filename={image.filename}
                  imageUrl={image.image_url}
                  prediction={image.prediction}
                  confidence={image.confidence}
                />
              ))}
            </section>
          </div>
        )}
      </section>

      <footer className="text-center text-sm text-slate-500">
        <p>Frontend connected to backend via <code className="rounded-md bg-slate-900 px-2 py-1">POST /analyze/</code>.</p>
      </footer>
    </main>
  )
}
